import asyncio
from fastmcp import Client
import ollama
import json
import sys
from typing import Any, Dict, List, Optional

class OllamaAgentClient:
    def __init__(self, server_url: str, ollama_model: str = "gpt-oss:20b"):
        self.server_url = server_url
        self.ollama_model = ollama_model
        self.client = Client(server_url)
        self.ollama_tools: List[Dict[str, Any]] = [] # To store discovered tools

    async def _discover_tools(self):
        """Discovers tools from the fastmcp server and converts them to Ollama format."""
        print("Connected! Discovering tools...")
        self.ollama_tools = [] # Clear tools on each discovery attempt
        fastmcp_tools = await self.client.list_tools()
        
        for tool_obj in fastmcp_tools:
            # The tool_obj here is a Tool object from fastmcp.
            # It has .name, .description, and crucially, .inputSchema.
            
            ollama_parameters = tool_obj.inputSchema # Directly use inputSchema
            
            # Ensure 'type', 'properties', 'required' are present if inputSchema is empty
            if not ollama_parameters:
                ollama_parameters = {
                    'type': 'object',
                    'properties': {},
                    'required': [],
                }
            
            self.ollama_tools.append({
                'type': 'function',
                'function': {
                    'name': tool_obj.name,
                    'description': tool_obj.description or f"A tool named {tool_obj.name}",
                    'parameters': ollama_parameters
                }
            })
        
        print(f"Discovered {len(self.ollama_tools)} tools.")
        print("Type 'exit' or press Ctrl+C to quit.")

    async def _chat_with_ollama(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Sends messages to Ollama and returns the response."""
        # Send to Ollama (Initial or Follow-up)
        print("--- Sending to Ollama ---")
        print("Tools:", json.dumps(self.ollama_tools, indent=2))
        print("Messages:", json.dumps([m.model_dump() if hasattr(m, 'model_dump') else m for m in messages], indent=2))

        response = ollama.chat(
            model=self.ollama_model,
            messages=messages,
            tools=self.ollama_tools
        )
        return response

    async def _execute_tool(self, function_name: str, function_args: Dict[str, Any]) -> str:
        """Executes a tool on the fastmcp server and returns its output."""
        print(f"Agent wants to execute tool: {function_name} with arguments: {function_args}")
        
        try:
            tool_result_obj = await self.client.call_tool(function_name, function_args)
            if tool_result_obj.content and isinstance(tool_result_obj.content, list):
                tool_output = tool_result_obj.content[0].text
            else:
                tool_output = str(tool_result_obj.data)
        except Exception as e:
            print(f"Error executing tool {function_name}: {e}")
            tool_output = f"Error: {e}"
        return tool_output

    async def run(self):
        """Runs the main interactive chat loop."""
        print("Connecting to MCP Agent...")

        retries = 5
        for i in range(retries):
            try:
                async with self.client:
                    await self._discover_tools()
                    
                    messages: List[Dict[str, Any]] = [] # Conversation history
                    
                    while True:
                        try:
                            prompt = await asyncio.to_thread(input, "You: ")
                            if prompt.lower() == 'exit':
                                break
                            
                            if not prompt:
                                continue

                            messages.append({'role': 'user', 'content': prompt})

                            response = await self._chat_with_ollama(messages)
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

                                response = await self._chat_with_ollama(messages)
                                messages.append(response['message'])

                            print(f"Agent: {response['message']['content']}")

                        except (KeyboardInterrupt, EOFError):
                            break
                    
                    return # Exit the function successfully after chat loop

            except Exception as e:
                if i < retries - 1:
                    print(f"Connection failed, retrying in 2 seconds...")
                    await asyncio.sleep(2)
                else:
                    print(f"Failed to connect after {retries} attempts: {e}")
        
        print("\nConnection closed.")

if __name__ == "__main__":
    # This is needed to make input() work correctly with asyncio on Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    client_app = OllamaAgentClient(server_url="http://localhost:8000/mcp", ollama_model="gpt-oss:20b")
    asyncio.run(client_app.run())