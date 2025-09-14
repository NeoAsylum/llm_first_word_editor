import argparse
import asyncio
import os
from fastmcp import Client

import json
import sys
from dotenv import load_dotenv
from typing import Any, Dict, List, Optional
import logging
from google.genai import types
from google import genai

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GeminiAgentClient:
    def __init__(self, server_url: str, gemini_model: str = "gemini-2.5-flash-lite"):
        self.server_url = server_url
        self.gemini_model = gemini_model
        self.client = Client(server_url)
        self.gemini_client = self._initialize_gemini_client()
        # self.chat_session is no longer needed for this approach

    def _initialize_gemini_client(self):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set for Gemini API.")
        return genai.Client(api_key=api_key)

    async def _chat_with_llm(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        logging.debug("--- Sending to Gemini ---")

        # Convert messages to Gemini's Content format for generate_content
        gemini_contents = []
        for msg in messages:
            if msg['role'] == 'user':
                gemini_contents.append(types.Content(role="user", parts=[types.Part(text=msg['content'])]))
            elif msg['role'] == 'assistant':
                if msg.get('tool_calls'):
                    tool_code_parts = []
                    for tool_call in msg['tool_calls']:
                        function_name = tool_call['function']['name']
                        function_args = tool_call['function']["arguments"]
                        tool_code_parts.append(types.Part(function_call=types.FunctionCall(name=function_name, args=function_args)))
                    gemini_contents.append(types.Content(role="model", parts=tool_code_parts))
                else:
                    gemini_contents.append(types.Content(role="model", parts=[types.Part(text=msg['content'])]))
            elif msg['role'] == 'tool':
                # For tool responses, the role should be 'function' and content should be the tool output
                # The previous message should contain the tool_calls
                if messages and messages[-1]['role'] == 'assistant' and messages[-1].get('tool_calls'):
                    tool_name_for_response = messages[-1]['tool_calls'][0]['function']['name']
                    gemini_contents.append(types.Content(role="function", parts=[types.Part(function_response=types.FunctionResponse(name=tool_name_for_response, response=msg['content']))]))
                else:
                    logging.warning("Tool output received without preceding assistant tool call.")
                    gemini_contents.append(types.Content(role="function", parts=[types.Part(text=msg['content'])]))

        response = await self.gemini_client.aio.models.generate_content(
            model=self.gemini_model,
            contents=gemini_contents,
            config=types.GenerateContentConfig(
                tools=[self.client.session],  # Pass the FastMCP client session
            ),
        )

        full_response_content = response.text
        tool_calls_from_gemini = []

        # Extract tool calls from the response if any
        if response.function_calls:
            for fc in response.function_calls:
                tool_calls_from_gemini.append({
                    'function': {
                        'name': fc.name,
                        'arguments': fc.args
                    }
                })

        gemini_response = {
            'message': {
                'role': 'assistant',
                'content': full_response_content,
            }
        }
        if tool_calls_from_gemini:
            gemini_response['message']['tool_calls'] = tool_calls_from_gemini

        return gemini_response

    async def _execute_tool(self, function_name: str, function_args: Dict[str, Any]) -> Any: # Change return type to Any
        """Executes a tool on the fastmcp server and returns its output."""
        logging.info(f"Agent wants to execute tool: {function_name} with arguments: {function_args}")
        
        try:
            tool_result_obj = await self.client.call_tool(function_name, function_args)
            # If tool_result_obj.data is not None, return it directly.
            # Otherwise, return an empty string or a default message.
            if tool_result_obj.data is not None:
                return tool_result_obj.data
            elif tool_result_obj.content and isinstance(tool_result_obj.content, list):
                return tool_result_obj.content[0].text # Still return text if it's specifically text content
            else:
                return "" # Return empty string if no meaningful data or content
        except Exception as e:
            logging.error(f"Error executing tool {function_name}: {e}")
            return f"Error: {e}" # Return error message as string

    async def run(self):
        """Runs the main interactive chat loop."""
        logging.info("Connecting to MCP Agent...")

        retries = 5
        for i in range(retries):
            try:
                async with self.client:
                    # No need to discover tools explicitly for Gemini, as the session is passed
                    # However, we still need to ensure the client is connected and session is ready
                    # The client.session will be available after async with self.client:
                    
                    messages: List[Dict[str, Any]] = [] # Conversation history
                    
                    while True:
                        try:
                            prompt = await asyncio.to_thread(input, "You: ")
                            if prompt.lower() == 'exit':
                                break
                            
                            if not prompt:
                                continue

                            messages.append({'role': 'user', 'content': prompt})

                            try:
                                response = await self._chat_with_llm(messages)
                                logging.debug("LLM Response: %s", json.dumps(response, indent=2))
                                messages.append(response['message'])
                                
                                while response['message'].get('tool_calls'):
                                    tool_calls = response['message']['tool_calls']
                                    
                                    for tool_call in tool_calls:
                                        function_name = tool_call['function']['name']
                                        function_args = tool_call['function']['arguments']
                                        
                                        tool_output = await self._execute_tool(function_name, function_args)

                                        messages.append({
                                            'role': 'tool',
                                            'content': tool_output,
                                        })

                                    response = await self._chat_with_llm(messages)
                                    logging.debug("LLM Response after tool execution: %s", json.dumps(response, indent=2))
                                    messages.append(response['message'])

                                logging.info(f"Agent: {response['message']['content']}")
                            except Exception as chat_e:
                                logging.error(f"Error during chat interaction: {chat_e}", exc_info=True)
                                # Optionally, re-raise or break the loop if the error is critical
                                break

                        except (KeyboardInterrupt, EOFError):
                            break
                    
                    return # Exit the function successfully after chat loop

            except Exception as e:
                if i < retries - 1:
                    logging.warning(f"Connection failed, retrying in 2 seconds...")
                    await asyncio.sleep(2)
                else:
                    logging.error(f"Failed to connect after {retries} attempts: {e}")
        
        logging.info("\nConnection closed.")

if __name__ == "__main__":
    # This is needed to make input() work correctly with asyncio on Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    parser = argparse.ArgumentParser(description="Run the Gemini Agent Client.")
    parser.add_argument("--gemini_model", type=str, default="gemini-2.5-flash-lite", help="Gemini model to use.")
    args = parser.parse_args()

    client_app = GeminiAgentClient(server_url="http://localhost:8000/mcp", 
                                gemini_model=args.gemini_model)
    asyncio.run(client_app.run())