import json
import urllib.request
from fastmcp import FastMCP

# Use a single FastMCP instance
mcp = FastMCP(name="My MCP Server")

@mcp.resource("mcp://addresses")
def addresses() -> dict:
    """A resource containing addresses of people mapped to their names."""
    return ADDRESS_DATA
# -------------------------


# --- Editor Tools ---
EDITOR_API_URL = "http://localhost:8001"

def get_document_content() -> str:
    """Helper function to get the current document content from the editor server."""
    try:
        with urllib.request.urlopen(f"{EDITOR_API_URL}/document") as response:
            if response.status == 200:
                return json.loads(response.read().decode())['content']
            else:
                return f"Error: Received status {response.status}"
    except Exception as e:
        return f"Error fetching document: {e}"

@mcp.tool
def get_document() -> str:
    """Gets the current content of the document."""
    return get_document_content()

@mcp.tool
def bold(start: int, end: int) -> str:
    """Applies bold formatting to a range of text in the document."""
    req = urllib.request.Request(
        f"{EDITOR_API_URL}/format/bold",
        data=json.dumps({"start": start, "end": end}).encode(),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                return "Bold formatting applied."
            else:
                return f"Error: Received status {response.status}"
    except Exception as e:
        return f"Error applying bold: {e}"

@mcp.tool
def italic(start: int, end: int) -> str:
    """Applies italic formatting to a range of text in the document."""
    req = urllib.request.Request(
        f"{EDITOR_API_URL}/format/italic",
        data=json.dumps({"start": start, "end": end}).encode(),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                return "Italic formatting applied."
            else:
                return f"Error: Received status {response.status}"
    except Exception as e:
        return f"Error applying italic: {e}"

@mcp.tool
def find(search_term: str) -> str:
    """Finds all occurrences of a search term in the document."""
    req = urllib.request.Request(
        f"{EDITOR_API_URL}/find",
        data=json.dumps({"search_term": search_term}).encode(),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                if data['occurrences']:
                    return f"Found at positions: {data['occurrences']}"
                else:
                    return "No occurrences found."
            else:
                return f"Error: Received status {response.status}"
    except Exception as e:
        return f"Error finding text: {e}"

@mcp.tool
def insert(pos: int, text: str) -> str:
    """Inserts text at a given position in the document."""
    req = urllib.request.Request(
        f"{EDITOR_API_URL}/insert",
        data=json.dumps({"pos": pos, "text": text}).encode(),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                return "Text inserted."
            else:
                return f"Error: Received status {response.status}"
    except Exception as e:
        return f"Error inserting text: {e}"

@mcp.tool
def delete(start: int, end: int) -> str:
    """Deletes text in a given range in the document."""
    req = urllib.request.Request(
        f"{EDITOR_API_URL}/delete",
        data=json.dumps({"start": start, "end": end}).encode(),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                return "Text deleted."
            else:
                return f"Error: Received status {response.status}"
    except Exception as e:
        return f"Error deleting text: {e}"

if __name__ == "__main__":
    mcp.run(transport="http", port=8000)
