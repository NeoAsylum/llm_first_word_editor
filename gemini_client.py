import argparse
import asyncio
import os
from fastmcp import Client

import json
import sys
from dotenv import load_dotenv
from typing import Any, Dict, List
import logging
from google.genai import types
from google import genai

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(message)s",
    filename="logfile.txt",
    filemode="w",
)

# Console handler to show only INFO and above
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# Use a simpler format for the console
console_formatter = logging.Formatter("%(message)s")
console.setFormatter(console_formatter)
logging.getLogger("").addHandler(console)

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("fastmcp").setLevel(logging.ERROR)
logging.getLogger("google.genai").setLevel(logging.ERROR)


class GeminiAgentClient:
    def __init__(
        self,
        server_url: str,
        gemini_model: str = "gemini-2.5-flash",
        system_prompt: str = None,
    ):
        self.server_url = server_url
        self.gemini_model = gemini_model
        self.client = Client(server_url)
        self.gemini_client = self._initialize_gemini_client()
        self.system_prompt = system_prompt

    def _initialize_gemini_client(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable not set for Gemini API."
            )
        return genai.Client(api_key=api_key)

    def _handle_user_message(self, msg: Dict[str, Any]) -> types.Content:
        return types.Content(role="user", parts=[types.Part(text=msg["content"])])

    def _handle_assistant_message(self, msg: Dict[str, Any]) -> types.Content:
        if msg.get("tool_calls"):
            tool_code_parts = []
            for tool_call in msg["tool_calls"]:
                function_name = tool_call["function"]["name"]
                function_args = tool_call["function"]["arguments"]
                tool_code_parts.append(
                    types.Part(
                        function_call=types.FunctionCall(
                            name=function_name, args=function_args
                        )
                    )
                )
            return types.Content(role="model", parts=tool_code_parts)
        else:
            return types.Content(role="model", parts=[types.Part(text=msg["content"])])

    def _handle_tool_message(
        self,
        msg: Dict[str, Any],
        prev_msg: Dict[str, Any] | None,
    ) -> types.Content:
        if prev_msg and prev_msg["role"] == "assistant" and prev_msg.get("tool_calls"):
            tool_name_for_response = prev_msg["tool_calls"][0]["function"]["name"]
            return types.Content(
                role="function",
                parts=[
                    types.Part(
                        function_response=types.FunctionResponse(
                            name=tool_name_for_response,
                            response=msg["content"],
                        )
                    )
                ],
            )
        else:
            # Even if there is no preceding tool call, we still need to handle the message
            return types.Content(
                role="function", parts=[types.Part(text=msg["content"])]
            )

    def _convert_messages_to_gemini_content(
        self,
        messages: List[Dict[str, Any]],
    ) -> List[types.Content]:
        gemini_contents = []
        for i, msg in enumerate(messages):
            role = msg["role"]
            if role == "user":
                gemini_contents.append(self._handle_user_message(msg))
            elif role == "assistant":
                gemini_contents.append(self._handle_assistant_message(msg))
            elif role == "tool":
                prev_msg = messages[i - 1] if i > 0 else None
                gemini_contents.append(self._handle_tool_message(msg, prev_msg))
            else:
                logging.warning(f"Unknown role: {role}")
        return gemini_contents

    async def _chat_with_llm(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        logging.debug("--- Sending to Gemini ---")
        gemini_contents = self._convert_messages_to_gemini_content(messages)

        try:
            response = await self.gemini_client.aio.models.generate_content(
                model=self.gemini_model,
                contents=gemini_contents,
                config=types.GenerateContentConfig(
                    tools=[self.client.session], system_instruction=self.system_prompt
                ),
            )
            full_response_content = response.text
            tool_calls_from_gemini = []

            if response.function_calls:
                for fc in response.function_calls:
                    tool_calls_from_gemini.append(
                        {"function": {"name": fc.name, "arguments": fc.args}}
                    )

            gemini_response = {
                "message": {"role": "assistant", "content": full_response_content}
            }
            if tool_calls_from_gemini:
                gemini_response["message"]["tool_calls"] = tool_calls_from_gemini

            return gemini_response

        except genai.errors.ServerError as e:
            logging.error(f"Error communicating with Gemini API: {e}", exc_info=True)
            return {
                "message": {
                    "role": "assistant",
                    "content": "Agent: I encountered an error communicating with the Gemini API. "
                    "This might be due to a very large input. Please try a shorter "
                    "input or rephrase your request.",
                }
            }
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}", exc_info=True)
            return {
                "message": {
                    "role": "assistant",
                    "content": "Agent: An unexpected error occurred. Please try again.",
                }
            }

    async def run(self):
        """Runs the main interactive chat loop."""
        logging.info("Connecting to MCP Agent...")
        try:
            async with self.client:
                messages: List[Dict[str, Any]] = []
                while True:
                    try:
                        prompt = await asyncio.to_thread(input, "\nYou: ")
                        if prompt.lower() == "exit":
                            break
                        if not prompt:
                            continue

                        messages.append({"role": "user", "content": prompt})
                        response = await self._chat_with_llm(messages)
                        logging.debug(
                            "LLM Response: %s", json.dumps(response, indent=2)
                        )
                        messages.append(response["message"])

                        logging.info(f"Agent: {response['message']['content']}")

                    except (KeyboardInterrupt, EOFError):
                        break
        except Exception as e:
            logging.error(f"An error occurred: {e}", exc_info=True)
        finally:
            logging.info("\nConnection closed.")


async def main():
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    load_dotenv()

    parser = argparse.ArgumentParser(description="Run the Gemini Agent Client.")
    parser.add_argument(
        "--gemini_model",
        type=str,
        default="gemini-2.5-flash",
        help="Gemini model to use.",
    )
    parser.add_argument(
        "--system_prompt",
        type=str,
        default="You are a helpful assistant. You are the user interface to a word style document editor. You have access to multiple model context protocol tools via a mcp server that allow you to do the users bidding and edit this document. The user can see the document in real time, but can only interact with it through you. He can also not see the tool output, so you have to show him the return values of the tools you call. Always use get_text initially to understand file content. Use get_html to understand file structure. Also, when the user asks you for something use your tools to fullfill his request. Don't ask him for additional information. Get the information yourself using the tools provided.",
        help="The system prompt to use.",
    )
    args = parser.parse_args()

    client_app = GeminiAgentClient(
        server_url=os.getenv("SERVER_URL", "http://localhost:8000/mcp"),
        gemini_model=args.gemini_model,
        system_prompt=args.system_prompt,
    )
    await client_app.run()


if __name__ == "__main__":
    asyncio.run(main())
