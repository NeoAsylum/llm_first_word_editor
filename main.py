import json
import urllib.request
from fastmcp import FastMCP
from typing import List, Dict, Any

# Use a single FastMCP instance
mcp = FastMCP(name="My MCP Server")

# --- Editor Tools ---
EDITOR_API_URL = "http://localhost:8001"

def _json_to_markdown(content_list: List[Dict[str, Any]]) -> str:
    """Converts a list of stringObjects (as dicts) to a markdown string."""
    md_string = ""
    for item in content_list:
        text = item.get('content', '')
        if item.get('bold'):
            text = f"**{text}**"
        if item.get('italic'):
            text = f"*{text}*"
        md_string += text
    return md_string

@mcp.tool
def get_document() -> str:
    """Gets the current content of the document."""
    try:
        with urllib.request.urlopen(f"{EDITOR_API_URL}/document") as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                return _json_to_markdown(data)
            else:
                return f"Error: Received status {response.status}"
    except Exception as e:
        return f"Error fetching document: {e}"

@mcp.tool
def bold(so_id: int) -> str:
    """Applies bold formatting to a stringObject by its ID."""
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
    """Applies italic formatting to a stringObject by its ID."""
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
def find(search_term: str) -> str:
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
                if data:
                    output = "Found at positions:\n"
                    for item in data:
                        output += f"  ID: {item.get('id')}, Indices: {item.get('indices')}\n"
                    return output
                else:
                    return "No occurrences found."
            else:
                return f"Error: Received status {response.status}"
    except Exception as e:
        return f"Error finding text: {e}"

@mcp.tool
def insert(so_content: str, index: int, bold: bool = False, italic: bool = False) -> str:
    """Inserts a new stringObject at a given index in the document content."""
    new_so = {"content": so_content, "bold": bold, "italic": italic}
    req = urllib.request.Request(
        f"{EDITOR_API_URL}/document/insert_object",
        data=json.dumps({"so": new_so, "index": index}).encode(),
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
    """Deletes a stringObject by its ID from the document content."""
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
def get_header() -> str:
    """Gets the current content of the header."""
    try:
        with urllib.request.urlopen(f"{EDITOR_API_URL}/header") as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                return _json_to_markdown([data]) # Header is a single stringObject
            else:
                return f"Error: Received status {response.status}"
    except Exception as e:
        return f"Error fetching header: {e}"

@mcp.tool
def set_header(content: str, bold: bool = False, italic: bool = False) -> str:
    """Sets the content of the header."""
    new_header_so = {"content": content, "bold": bold, "italic": italic}
    req = urllib.request.Request(
        f"{EDITOR_API_URL}/header",
        data=json.dumps({"header": new_header_so}).encode(),
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
def get_footer() -> str:
    """Gets the current content of the footer."""
    try:
        with urllib.request.urlopen(f"{EDITOR_API_URL}/footer") as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                return _json_to_markdown([data]) # Footer is a single stringObject
            else:
                return f"Error: Received status {response.status}"
    except Exception as e:
        return f"Error fetching footer: {e}"

@mcp.tool
def set_footer(content: str, bold: bool = False, italic: bool = False) -> str:
    """Sets the content of the footer."""
    new_footer_so = {"content": content, "bold": bold, "italic": italic}
    req = urllib.request.Request(
        f"{EDITOR_API_URL}/footer",
        data=json.dumps({"footer": new_footer_so}).encode(),
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