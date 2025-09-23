# LLM First Word Editor

This project is a web-based word processor that is controlled by a Large Language Model (LLM) through a tool-based interface. The user can interact with the word processor by giving commands to a Gemini-based agent in natural language.

## Features

- Create and modify documents using natural language commands.
- Format text with **bold**, *italic*, subscript, and superscript styles.
- Set document margins (left, right, top, bottom).
- Find and replace text.
- Save and load documents.
- Live rendering of the document in a web browser.

## Project Structure

```
├── .gitignore
├── class_diagram.puml
├── gemini_client.py
├── logfile.txt
├── mcp_server_main.py
├── paragraph_log.txt
├── README.md
├── starte_server_gemini.cmd
├── word_processor_server.py
├── saves
│   ├── Barnaby.txt
│   └── document_test.txt
└── word_processor
    ├── __init__.py
    ├── document.py
    ├── enums.py
    ├── index.html
    ├── paragraph.py
    └── __pycache__
```

## Architecture

The project has a unique architecture that separates the document model, the rendering, and the user interface.

-   **Word Processor Server (`word_processor_server.py`):** A FastAPI server that manages the document's content. It exposes a REST API to create, modify, format, save, and load documents. It uses the `Document` class to represent the document in memory.

-   **Document Model (`word_processor/document.py`, `word_processor/paragraph.py`):** The document is represented by a `Document` class that contains a list of `Paragraph` objects. Each `Paragraph` has content and formatting attributes (bold, italic, etc.). This granular structure allows for fine-grained control over formatting.

-   **MCP Server (`mcp_server_main.py`):** A `FastMCP` server that acts as a bridge between the LLM and the Word Processor Server. It exposes the Word Processor's API as tools that the LLM can use. It translates the LLM's tool calls into HTTP requests to the Word Processor Server.

-   **Gemini Client (`gemini_client.py`):** A command-line interface that allows the user to interact with the Gemini agent. The user's prompts are sent to the Gemini LLM (defaulting to `gemini-1.5-flash`), which then decides which tool to use to manipulate the document.

-   **Web Interface (`word_processor/index.html`):** A simple HTML page that displays the rendered document. It fetches the document content from the Word Processor Server and renders it as HTML, updating automatically.

## How it Works

1.  **Start the servers:** Run the `starte_server_gemini.cmd` script. This will start both the Word Processor Server and the MCP Server in separate windows.
2.  **Start the client:** Run the `gemini_client.py` script. This will open a command-line interface to interact with the Gemini agent.
3.  **Interact with the agent:** Type commands in the Gemini Client console, for example:
    -   "insert 'Hello World' at the beginning of the document"
    -   "make the first word bold"
    -   "find the word 'sample'"
    -   "save the document as my_document.txt"
    -   "set the left margin to 20mm"
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
    -   Run `gemini_client.py` to start the client.

## Available Tools

The following tools are available for the LLM to use:

-   `get_document()`: Retrieves the entire document's content.
-   `insert_string(text: str, paragraph_index: int, string_index: int)`: Inserts a string of text into a specific paragraph at a given index.
-   `switch_formatting(paragraph_index: int, index: int, length: int, formatting_type: FormattingType)`: Toggles a specific formatting style (e.g., bold, italic) on a segment of text.
-   `find(search_term: str)`: Searches the entire document for a given search term.
-   `delete_substring(paragraph_index: int, string_index: int, length: int)`: Deletes a substring from a paragraph.
-   `save_document(filename: str)`: Saves the current state of the document to a file.
-   `load_document(filename: str)`: Loads a document from a file.
-   `set_margin(margin_type: MarginType, value_mm: int)`: Sets a specific margin for the document.