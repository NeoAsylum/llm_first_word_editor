import os
from fastmcp import Client

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
        self.system_prompt = "Always use get_text to gain an understanding of the document before doing anything. Always use find before any index based tool call. Alls index operations start at 0. Always use get_html before doing anything formatting related. You should often use all three get_html, find and get_text before doing anything. The user can see the document, but only interact with it by using you. After changing something you should verify the change using a tool call. ALWAYS USE FIND FOR INDEX BASED OPERATIONS, BECAUSE YOUR INDEX WILL BE OFF IF YOU DONT. DON'T DELETE OR INSERT OR SWITCH FORMAT WITHOUT FIND FIRST."



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
            async with self.client:
                response = await self.gemini_client.aio.models.generate_content(
                    model=self.gemini_model,
                    contents=gemini_contents,
                    config=types.GenerateContentConfig(
                        tools=[self.client.session],
                        automatic_function_calling=types.AutomaticFunctionCallingConfig(
                            maximum_remote_calls=20
                        ),
                        system_instruction=self.system_prompt,
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
