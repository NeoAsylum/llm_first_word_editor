import json
import urllib.request
from datetime import datetime
from fastmcp import FastMCP
from typing import List, Optional
from pydantic import BaseModel
from word_processor.enums import FormattingType, MarginType

# Use a single FastMCP instance
mcp = FastMCP(name="My MCP Server")
# include_tags
# set[str] | None
# Only expose components with at least one matching tag
# ​
# exclude_tags
# set[str] | None
# Hide components with any matching tag


# --- Pydantic Models ---
class Paragraph(BaseModel):
    start_index: int
    end_index: int
    content: str
    bold: bool = False
    italic: bool = False
    lowerscript: bool = False
    superscript: bool = False


class FindResult(BaseModel):
    locations: List[tuple[int, int]]


class MessageResponse(BaseModel):
    message: str


# --- Editor Tools ---
EDITOR_API_URL = "http://localhost:8001"


@mcp.tool
def get_text() -> str:
    """
    Retrieves the entire document's content as a single plain text string.

    This tool is useful for quickly reading the document's text without any formatting information. Most operations work simply by using the plain text start_index and end_index.
    """
    print(f"{datetime.now()} - Calling method: get_text", flush=True)

    try:
        with urllib.request.urlopen(f"{EDITOR_API_URL}/document/text_only") as response:
            if response.status == 200:
                output = response.read().decode()
                print(f"Output: {output}", flush=True)
                return output
            else:
                return ""
    except Exception as e:
        print(f"Error in get_text: {e}")
        return ""


@mcp.tool
def get_html() -> str:
    """
    Retrieves the HTML representation of the document.

    This tool is useful for understanding the visual layout and formatting of the document as it would appear in a web browser.
    """
    print(f"{datetime.now()} - Calling method: get_html", flush=True)

    try:
        with urllib.request.urlopen(f"{EDITOR_API_URL}/document/html") as response:
            if response.status == 200:
                output = response.read().decode()
                print(f"Output: {output}", flush=True)
                return output
            else:
                return ""
    except Exception as e:
        print(f"Error in get_html: {e}")
        return ""


@mcp.tool
def insert_string(
    text: str,
    index: int,
) -> MessageResponse:
    """
    Inserts a string of text into the document at a given character index.
    Always use get_text first and find to get the exact index.
    Insert \n for newline.
    To ensure text is inserted at the correct location, it is highly recommended to first use the 'find' and 'get_text' tool to get the precise 'index'.

    Args:
        text: The string of text to insert. Can include newline characters (\n).
        index: The character index within the document's content where the text should be inserted.
    """
    print(
        f"{datetime.now()} - Calling method: insert_string with parameters text: {text}, index: {index}",
        flush=True,
    )

    data = {
        "text": text,
        "index": index,
    }
    req = urllib.request.Request(
        f"{EDITOR_API_URL}/document/insert_string",
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                response_data = json.loads(response.read().decode())
                output = MessageResponse(**response_data)
                print(f"Output: {output}", flush=True)
                return output
            else:
                return MessageResponse(
                    message=f"Error: Received status {response.status}"
                )
    except Exception as e:
        return MessageResponse(message=f"Error inserting string: {e}")


@mcp.tool
def switch_formatting(
    start_index: int,
    end_index: int,
    formatting_type: FormattingType,
) -> MessageResponse:
    """
    Toggles a specific formatting style (e.g., bold, italic) on a segment of text. It is recommended to use find for the exact index and get_text for an overview.
    Always use get_text first.
    Args:
        start_index: The starting character index of the text segment to format.
        end_index: The ending character index of the text segment to format. This letter also gets formatted.
        formatting_type: The type of formatting to toggle. Valid options are: 'BOLD', 'ITALIC', 'LOWERSCRIPT', 'SUPERSCRIPT', 'TITLE', 'HEADING', 'SUBHEADING', 'BODY'.
    """
    print(
        f"{datetime.now()} - Calling method: switch_formatting with parameters start_index: {start_index}, end_index: {end_index}, formatting_type: {formatting_type}",
        flush=True,
    )

    data = {
        "start_index": start_index,
        "end_index": end_index,
        "formatting_type": formatting_type.value,
    }
    req = urllib.request.Request(
        f"{EDITOR_API_URL}/format/switch",
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                response_data = json.loads(response.read().decode())
                output = MessageResponse(**response_data)
                print(f"Output: {output}", flush=True)
                return output
            else:
                return MessageResponse(
                    message=f"Error: Received status {response.status}"
                )
    except Exception as e:
        return MessageResponse(message=f"Error applying formatting: {e}")


@mcp.tool
def find(search_term: str) -> FindResult:
    """
    Searches the entire document for a given search term and returns all occurrences.

    Returns a 'FindResult' object which contains:
    - 'locations': A list of tuples, where each tuple contains the 'start_index' and 'end_index' of a match.

    This tool is very useful for finding the exact coordinates ('start_index' and 'end_index') to use with other tools like 'insert_string' or 'switch_formatting'.

    Args:
        search_term: The text to search for in the document.
    """
    print(
        f"{datetime.now()} - Calling method: find with parameters search_term: {search_term}",
        flush=True,
    )

    req = urllib.request.Request(
        f"{EDITOR_API_URL}/document/find_in_body",
        data=json.dumps({"search_term": search_term}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                response_data = json.loads(response.read().decode())
                output = FindResult(**response_data)
                print(f"Output: {output}", flush=True)
                return output
            else:
                print(f"Error: Received status {response.status}")
                return None
    except Exception as e:
        print(f"Error finding text: {e}")
        return None


@mcp.tool
def delete_substring(start_index: int, end_index: int) -> MessageResponse:
    """
    Deletes a substring from the document.
    Always use get_text first and find to get the exact index.
    Use the 'find' or 'get_text' tool to get the correct 'start_index' and 'end_index' before using this tool.
    Incorrect indices may lead to unexpected behavior or errors.

    Args:
        start_index: The starting index of the substring to delete.
        end_index: The ending index of the substring to delete. This letter also gets deleted.
    """
    print(
        f"{datetime.now()} - Calling method: delete_substring with parameters start_index: {start_index}, end_index: {end_index}",
        flush=True,
    )

    data = {
        "start_index": start_index,
        "end_index": end_index,
    }
    req = urllib.request.Request(
        f"{EDITOR_API_URL}/document/delete_substring",
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                response_data = json.loads(response.read().decode())
                output = MessageResponse(**response_data)
                print(f"Output: {output}", flush=True)
                return output
            else:
                return MessageResponse(
                    message=f"Error: Received status {response.status}"
                )
    except Exception as e:
        return MessageResponse(message=f"Error deleting substring: {e}")


@mcp.tool
def save_document(filename: str) -> MessageResponse:
    """
    Saves the current state of the document to a file in JSON format.

    The file will be saved in a pre-configured 'saves' directory. You only need to provide the filename, not the full path.

    Args:
        filename: The name of the file to save the document as (e.g., 'my_document.txt').
    """
    print(
        f"{datetime.now()} - Calling method: save_document with parameters filename: {filename}",
        flush=True,
    )

    req = urllib.request.Request(
        f"{EDITOR_API_URL}/document/save",
        data=json.dumps({"filename": filename}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                response_data = json.loads(response.read().decode())
                output = MessageResponse(**response_data)
                print(f"Output: {output}", flush=True)
                return output
            else:
                return MessageResponse(
                    message=f"Error: Received status {response.status}"
                )
    except Exception as e:
        return MessageResponse(message=f"Error saving document: {e}")


@mcp.tool
def load_document(filename: str) -> MessageResponse:
    """
    Loads a document from a JSON file, replacing the current document content.

    The file will be loaded from a pre-configured 'saves' directory. You only need to provide the filename, not the full path.

    Args:
        filename: The name of the file to load the document from (e.g., 'my_document.txt').
    """
    print(
        f"{datetime.now()} - Calling method: load_document with parameters filename: {filename}",
        flush=True,
    )

    req = urllib.request.Request(
        f"{EDITOR_API_URL}/document/load",
        data=json.dumps({"filename": filename}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                response_data = json.loads(response.read().decode())
                output = MessageResponse(**response_data)
                print(f"Output: {output}", flush=True)
                return output
            else:
                return MessageResponse(
                    message=f"Error: Received status {response.status}"
                )
    except Exception as e:
        return MessageResponse(message=f"Error loading document: {e}")


@mcp.tool
def set_margin(margin_type: MarginType, value_mm: int) -> MessageResponse:
    """
    Sets a specific margin for the document. The value is converted to cm internally.

    Args:
        margin_type: The type of margin to set. Valid options are: 'LEFT', 'RIGHT', 'TOP', 'BOTTOM'.
        value_mm: The value of the margin in millimeters.
    """
    print(
        f"{datetime.now()} - Calling method: set_margin with parameters margin_type: {margin_type}, value_mm: {value_mm}",
        flush=True,
    )
    data = {
        "margin_type": margin_type.value,
        "value_mm": value_mm,
    }
    req = urllib.request.Request(
        f"{EDITOR_API_URL}/document/set_margin",
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                response_data = json.loads(response.read().decode())
                output = MessageResponse(**response_data)
                print(f"Output: {output}", flush=True)
                return output
            else:
                return MessageResponse(
                    message=f"Error: Received status {response.status}"
                )
    except Exception as e:
        return MessageResponse(message=f"Error setting margin: {e}")


if __name__ == "__main__":
    print("Starting the MCP server now...", flush=True)
    mcp.run(transport="http", port=8000)
