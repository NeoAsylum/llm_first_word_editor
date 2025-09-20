import json
import urllib.request
from fastmcp import FastMCP
from typing import List, Optional
from pydantic import BaseModel
from word_processor.enums import FormattingType

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
    """Gets the current content of the document as a list of Paragraph objects.  A new "paragraph" begins whenever the formatting changes"""
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
def switch_formatting(
    paragraph_index: int,
    index: int,
    length: int,
    formatting_type: FormattingType,
) -> MessageResponse:
    """Applies or removes formatting to a substring of a Paragraph."""
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
    """Finds all occurrences of a search term in the document body. Returns an object with the length of the search term and a list of locations (paragraph_index, index_in_paragraph)."""
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
def insert(
    so_content: str,
    index: int,
    bold: bool = False,
    italic: bool = False,
    lowerscript: bool = False,
    superscript: bool = False,
) -> MessageResponse:
    """Inserts a new Paragraph at a given index in the document content."""
    new_word = {
        "content": so_content,
        "bold": bold,
        "italic": italic,
        "lowerscript": lowerscript,
        "superscript": superscript,
    }
    req = urllib.request.Request(
        f"{EDITOR_API_URL}/document/insert_string",
        data=json.dumps({"so": new_word, "index": index}).encode(),
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
        return MessageResponse(message=f"Error inserting object: {e}")


@mcp.tool
def delete(paragraph_index: int) -> MessageResponse:
    """Deletes a Paragraph by its index from the document content."""
    req = urllib.request.Request(
        f"{EDITOR_API_URL}/document/delete_paragraph/{paragraph_index}",
        headers={"Content-Type": "application/json"},
        method="DELETE",
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
        return MessageResponse(message=f"Error deleting object: {e}")


@mcp.tool
def save_document(filename: str) -> MessageResponse:
    """Saves the current document to a file."""
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
    """Loads a document from a file."""
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


if __name__ == "__main__":
    mcp.run(transport="http", port=8000)
