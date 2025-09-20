@echo off
call .\.venv\Scripts\activate.bat
echo Starting MCP Client and Server in new windows...
start "MCP Client" cmd /k "python gemini_client.py"
start "MCP Server" cmd /k "python mcp_server_main.py"