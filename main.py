import json
import urllib.request
from fastmcp import FastMCP
from typing import List, Optional, Literal
from pydantic import BaseModel

# Use a single FastMCP instance
mcp = FastMCP(name="My MCP Server")

# --- Pydantic Models ---
class Word(BaseModel):
    type: Literal['word'] = 'word'
    id: Optional[int] = None
    content: str
    bold: bool = False
    italic: bool = False
    lowerscript: bool = False
    superscript: bool = False

# --- Editor Tools ---
EDITOR_API_URL = "http://localhost:8001"

@mcp.tool
def get_document() -> List[Word]:
    """Gets the current content of the document as a list of Word objects."""
    try:
        with urllib.request.urlopen(f"{EDITOR_API_URL}/document") as response:
            if response.status == 200:
                content = json.loads(response.read().decode())
                return content
            else:
                return []
    except Exception as e:
        return []

@mcp.tool
def bold(so_id: int) -> str:
    """Applies bold formatting to a Word by its ID."""
    req = urllib.request.Request(
        f"{EDITOR_API_URL}/format/bold/{so_id}",
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                return f"Bold formatting applied to object {so_id}."
            else:
                return f"Error: Received status {response.status}"
    except Exception as e:
        return f"Error applying bold: {e}"

@mcp.tool
def italic(so_id: int) -> str:
    """Applies italic formatting to a Word by its ID."""
    req = urllib.request.Request(
        f"{EDITOR_API_URL}/format/italic/{so_id}",
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                return f"Italic formatting applied to object {so_id}."
            else:
                return f"Error: Received status {response.status}"
    except Exception as e:
        return f"Error applying italic: {e}"

@mcp.tool
def lowerscript(so_id: int) -> str:
    """Applies lowerscript formatting to a Word by its ID."""
    req = urllib.request.Request(
        f"{EDITOR_API_URL}/format/lowerscript/{so_id}",
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                return f"Lowerscript formatting applied to object {so_id}."
            else:
                return f"Error: Received status {response.status}"
    except Exception as e:
        return f"Error applying lowerscript: {e}"

@mcp.tool
def superscript(so_id: int) -> str:
    """Applies superscript formatting to a Word by its ID."""
    req = urllib.request.Request(
        f"{EDITOR_API_URL}/format/superscript/{so_id}",
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                return f"Superscript formatting applied to object {so_id}."
            else:
                return f"Error: Received status {response.status}"
    except Exception as e:
        return f"Error applying superscript: {e}"

@mcp.tool
def find(search_term: str) -> list[dict]: # Change return type hint
    """Finds all occurrences of a search term in the document body."""
    req = urllib.request.Request(
        f"{EDITOR_API_URL}/document/find_in_body",
        data=json.dumps({"search_term": search_term}).encode(),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                return data # Return the raw JSON data
            else:
                # Return an error structure that Gemini might understand
                return {"error": f"Received status {response.status}"}
    except Exception as e:
        return {"error": f"Error finding text: {e}"}

@mcp.tool
def insert(so_content: str, index: int, bold: bool = False, italic: bool = False, lowerscript: bool = False, superscript: bool = False) -> str:
    """Inserts a new Word at a given index in the document content."""
    new_word = {"content": so_content, "bold": bold, "italic": italic, "lowerscript": lowerscript, "superscript": superscript, "type": "word"}
    req = urllib.request.Request(
        f"{EDITOR_API_URL}/document/insert_object",
        data=json.dumps({"so": new_word, "index": index}).encode(),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                return "Object inserted."
            else:
                return f"Error: Received status {response.status}"
    except Exception as e:
        return f"Error inserting object: {e}"

@mcp.tool
def delete(so_id: int) -> str:
    """Deletes a Word by its ID from the document content."""
    req = urllib.request.Request(
        f"{EDITOR_API_URL}/document/delete_object/{so_id}",
        headers={'Content-Type': 'application/json'},
        method='DELETE'
    )
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                return f"Object with ID {so_id} deleted."
            else:
                return f"Error: Received status {response.status}"
    except Exception as e:
        return f"Error deleting object: {e}"

@mcp.tool
def get_header() -> List[Word]:
    """Gets the current content of the header as HTML."""
    try:
        with urllib.request.urlopen(f"{EDITOR_API_URL}/header") as response:
            if response.status == 200:
                return response.read().decode()
            else:
                return f"Error: Received status {response.status}"
    except Exception as e:
        return f"Error fetching header: {e}"

@mcp.tool
def set_header(content: str, bold: bool = False, italic: bool = False, lowerscript: bool = False, superscript: bool = False) -> str:
    """Sets the content of the header."""
    new_header_word = {"content": content, "bold": bold, "italic": italic, "lowerscript": lowerscript, "superscript": superscript, "type": "word"}
    req = urllib.request.Request(
        f"{EDITOR_API_URL}/header",
        data=json.dumps({"header": new_header_word}).encode(),
        headers={'Content-Type': 'application/json'},
        method='PUT'
    )
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                return "Header updated."
            else:
                return f"Error: Received status {response.status}"
    except Exception as e:
        return f"Error setting header: {e}"

@mcp.tool
def get_footer() -> List[Word]:
    """Gets the current content of the footer as HTML."""
    try:
        with urllib.request.urlopen(f"{EDITOR_API_URL}/footer/html") as response:
            if response.status == 200:
                return response.read().decode()
            else:
                return f"Error: Received status {response.status}"
    except Exception as e:
        return f"Error fetching footer: {e}"

@mcp.tool
def set_footer(content: str, bold: bool = False, italic: bool = False, lowerscript: bool = False, superscript: bool = False) -> str:
    """Sets the content of the footer."""
    new_footer_word = {"content": content, "bold": bold, "italic": italic, "lowerscript": lowerscript, "superscript": superscript, "type": "word"}
    req = urllib.request.Request(
        f"{EDITOR_API_URL}/footer",
        data=json.dumps({"footer": new_footer_word}).encode(),
        headers={'Content-Type': 'application/json'},
        method='PUT'
    )
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                return "Footer updated."
            else:
                return f"Error: Received status {response.status}"
    except Exception as e:
        return f"Error setting footer: {e}"


if __name__ == "__main__":
    mcp.run(transport="http", port=8000)