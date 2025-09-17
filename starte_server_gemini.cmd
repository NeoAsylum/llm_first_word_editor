@echo off
echo Starting MCP Client and Server in new windows...
start "MCP Client" cmd /k "c:\Users\adria\Downloads\mcp_server\starte_client_gemini.cmd"
start "MCP Server" cmd /k "call .\.venv\Scripts\activate.bat && python main.py"