from fastmcp import FastMCP

# Use a single FastMCP instance
mcp = FastMCP(name="My MCP Server")

# --- Address Resource ---
ADDRESS_DATA = {
    "Adrian": "123 Main St, Anytown, USA",
    "John Doe": "456 Oak Ave, Someplace, USA",
    "Jane Smith": "789 Pine Ln, Elsewhere, USA"
}

@mcp.resource("mcp://addresses")
def addresses() -> dict:
    """A resource containing addresses of people mapped to their names."""
    return ADDRESS_DATA
# -------------------------


# --- Tools ---
@mcp.tool
def greet(name: str) -> str:
    """Greets the user by name."""
    return f"Hello, {name}!"

@mcp.tool
def get_address(name: str) -> str:
    """Gets the address for a given name from the addresses resource."""
    return ADDRESS_DATA.get(name, f"Sorry, I don't have an address for {name}.")
# -------------------------


if __name__ == "__main__":
    mcp.run(transport="http", port=8000)
