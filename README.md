# LLM First Word Editor

This project is a web-based word processor that is controlled by a Large Language Model (LLM) through a tool-based interface. The user can interact with the word processor by giving commands to a Gemini-based agent in natural language.

## Architecture

The project has a unique architecture that separates the document model, the rendering, and the user interface.

-   **Word Processor Server (`word_processor_server.py`):** A FastAPI server that manages the document's content. It exposes a REST API to create, modify, format, save, and load documents.
-   **Document Model (`word_processor/document.py`, `word_processor/paragraph.py`):** The document is represented by a `Document` class that contains a list of `Paragraph` objects. Each `Paragraph` has content and formatting attributes (bold, italic, etc.).
-   **MCP Server (`mcp_server_main.py`):** A `FastMCP` server that acts as a bridge between the LLM and the Word Processor Server. It exposes the Word Processor's API as tools that the LLM can use.
-   **Gemini Client (`gemini_client.py`):** A command-line interface that allows the user to interact with the Gemini agent. The user's prompts are sent to the Gemini LLM, which then decides which tool to use to manipulate the document.
-   **Web Interface (`index.html`):** A simple HTML page that displays the rendered document. It fetches the document content from the Word Processor Server and renders it as HTML.

## How it Works

1.  **Start the servers:** Run the `starte_server_gemini.cmd` script. This will start both the Word Processor Server and the MCP Server in separate windows.
2.  **Start the client:** Run the `starte_client_gemini.cmd` script. This will open a command-line interface to interact with the Gemini agent.
3.  **Interact with the agent:** Type commands in the Gemini Client console, for example:
    -   "insert 'Hello World' at index 0"
    -   "make the first word bold"
    -   "save the document as my_document.txt"
4.  **View the document:** Open a web browser and navigate to `http://localhost:8001/` to see the live rendering of the document.

## Setup

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Set up Gemini API Key:**
    Create a `.env` file in the root directory and add your Gemini API key:
    ```
    GEMINI_API_KEY=your_api_key
    ```
3.  **Run the application:**
    -   Run `starte_server_gemini.cmd` to start the servers.
    -   Run `starte_client_gemini.cmd` to start the client.

## Files

-   `word_processor_server.py`: The main server for the word processor.
-   `mcp_server_main.py`: The server that exposes the tools to the LLM.
-   `gemini_client.py`: The command-line client for interacting with the LLM.
-   `word_processor/`: The package containing the document model and other related modules.
-   `saves/`: The directory where the documents are saved.
-   `starte_server_gemini.cmd`: The script to start the servers.
-   `starte_client_gemini.cmd`: The script to start the client.
-   `logfile.txt`: The log file for the Gemini client.
