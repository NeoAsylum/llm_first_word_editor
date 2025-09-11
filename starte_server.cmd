@echo off
echo Starting client in a new window...
start "MCP Client" cmd /k "c:\Users\adria\Downloads\mcp_server\starte_client.cmd"

echo Starting server in this window...
call .\.venv\Scripts\activate.bat
python main.py
