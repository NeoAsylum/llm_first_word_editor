import json
import urllib.request
from fastmcp import FastMCP
from typing import List, Optional
from pydantic import BaseModel
from word_processor.enums import FormattingType, MarginType

# Use a single FastMCP instance
mcp = FastMCP(name="My MCP Server")


# --- Pydantic Models ---
class Paragraph(BaseModel):
    content: str
    bold: bool = False
    italic: bool = False
    lowerscript: bool = False
    superscript: bool = False


class FindResult(BaseModel):
    length: int
    locations: List[tuple[int, int]]


class MessageResponse(BaseModel):
    message: str


# --- Editor Tools ---
EDITOR_API_URL = "http://localhost:8001"


@mcp.tool
def get_document() -> List[Paragraph]:
    """
    Retrieves the entire document's content. The document is represented as a list of 'Paragraph' objects.
    Each 'Paragraph' object has a 'content' (the text) and formatting properties (bold, italic, etc.).
    A new 'Paragraph' object is created whenever the text formatting changes.
    This allows for a structured representation of the document's content and styling.
    """
    try:
        with urllib.request.urlopen(f"{EDITOR_API_URL}/document") as response:
            if response.status == 200:
                content_data = json.loads(response.read().decode())
                return content_data
            else:
                return []
    except Exception as e:
        print(f"Error in get_document: {e}")
        return []


@mcp.tool
def insert_string(
    text: str,
    paragraph_index: int,
    string_index: int,
) -> MessageResponse:
    """
    Inserts a string of text into a specific paragraph at a given index.

    To ensure text is inserted at the correct location, it is highly recommended to first use the 'find' tool to get the precise paragraph_index and string_index for the desired insertion point.
    Incorrect indices may lead to unexpected behavior or errors.

    Args:
        text: The string of text to insert.
        paragraph_index: The index of the paragraph to insert the text into.
        string_index: The character index within the paragraph's content where the text should be inserted.
    """
    data = {
        "text": text,
        "paragraph_index": paragraph_index,
        "string_index": string_index,
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
                return MessageResponse(**response_data)
            else:
                return MessageResponse(
                    message=f"Error: Received status {response.status}"
                )
    except Exception as e:
        return MessageResponse(message=f"Error inserting string: {e}")


@mcp.tool
def switch_formatting(
    paragraph_index: int,
    index: int,
    length: int,
    formatting_type: FormattingType,
) -> MessageResponse:
    """
    Toggles a specific formatting style (e.g., bold, italic) on a segment of text within a paragraph.

    This function will apply the specified formatting if it's not present, or remove it if it is already applied.
    For example, if the text is already bold and you call this with 'BOLD', it will become not bold.

    Args:
        paragraph_index: The index of the paragraph to modify.
        index: The starting character index of the text segment to format.
        length: The number of characters in the text segment to format.
        formatting_type: The type of formatting to toggle. Valid options are: 'BOLD', 'ITALIC', 'LOWERSCRIPT', 'SUPERSCRIPT'.
    """
    data = {
        "paragraph_index": paragraph_index,
        "index": index,
        "length": length,
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
                return MessageResponse(**response_data)
            else:
                return MessageResponse(
                    message=f"Error: Received status {response.status}"
                )
    except Exception as e:
        return MessageResponse(message=f"Error applying formatting: {e}")


@mcp.tool
def find(search_term: str) -> Optional[FindResult]:
    """
    Searches the entire document for a given search term.

    Returns a 'FindResult' object which contains:
    - 'length': The character length of the search_term.
    - 'locations': A list of tuples, where each tuple contains the 'paragraph_index' and 'index_in_paragraph' of a match.

    This tool is very useful for finding the exact coordinates to use with other tools like 'insert_string' or 'switch_formatting'.
    It is recommended to use 'get_document' first to have an idea of the document's content.

    Args:
        search_term: The text to search for in the document.
    """
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
                return FindResult(**response_data)
            else:
                print(f"Error: Received status {response.status}")
                return None
    except Exception as e:
        print(f"Error finding text: {e}")
        return None


@mcp.tool
def delete_substring(paragraph_index: int, string_index: int, length: int) -> MessageResponse:
    """
    Deletes a substring from a paragraph.
    Use the find tool to find the paragraph and index of a substring to delete. Correct paragraph and index can change in between every action.
    Args:
        paragraph_index: The index of the paragraph to delete from.
        string_index: The starting index of the substring to delete.
        length: The length of the substring to delete.
    """
    data = {
        "paragraph_index": paragraph_index,
        "string_index": string_index,
        "length": length,
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
                return MessageResponse(**response_data)
            else:
                return MessageResponse(
                    message=f"Error: Received status {response.status}"
                )
    except Exception as e:
        return MessageResponse(message=f"Error deleting substring: {e}")


@mcp.tool
def save_document(filename: str) -> MessageResponse:
    """
    Saves the current state of the document to a file.

    The file will be saved in a pre-configured 'saves' directory.
    You only need to provide the filename, not the full path.

    Args:
        filename: The name of the file to save the document as (e.g., 'my_document.txt').
    """
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
                return MessageResponse(**response_data)
            else:
                return MessageResponse(
                    message=f"Error: Received status {response.status}"
                )
    except Exception as e:
        return MessageResponse(message=f"Error saving document: {e}")


@mcp.tool
def load_document(filename: str) -> MessageResponse:
    """
    Loads a document from a file, replacing the current document content.

    The file will be loaded from a pre-configured 'saves' directory.
    You only need to provide the filename, not the full path.

    Args:
        filename: The name of the file to load the document from (e.g., 'my_document.txt').
    """
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
                return MessageResponse(**response_data)
            else:
                return MessageResponse(
                    message=f"Error: Received status {response.status}"
                )
    except Exception as e:
        return MessageResponse(message=f"Error loading document: {e}")

@mcp.tool
def set_margin(margin_type: MarginType, value_mm: int) -> MessageResponse:
    """
    Sets a specific margin for the document.

    Args:
        margin_type: The type of margin to set. Valid options are: 'LEFT', 'RIGHT', 'TOP', 'BOTTOM'.
        value_mm: The value of the margin in millimeters.
    """
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
                return MessageResponse(**response_data)
            else:
                return MessageResponse(
                    message=f"Error: Received status {response.status}"
                )
    except Exception as e:
        return MessageResponse(message=f"Error setting margin: {e}")

if __name__ == "__main__":
    mcp.run(transport="http", port=8000)
