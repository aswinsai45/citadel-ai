import os
from mcp.server.fastmcp import FastMCP

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

mcp = FastMCP("citadel-docs")


@mcp.tool()
def search_docs(query: str) -> str:
    """Return filenames of internal documents matching the query words."""
    words = query.lower().split()
    scored = []
    for name in os.listdir(DATA_DIR):
        with open(os.path.join(DATA_DIR, name), encoding="utf-8") as f:
            text = f.read().lower()
        score = sum(1 for w in words if w in text)
        if score:
            scored.append((score, name))
    scored.sort(reverse=True)
    return ", ".join(name for _, name in scored) if scored else "No matching documents."


@mcp.tool()
def read_file(name: str) -> str:
    """Return the full text of an internal document by filename."""
    with open(os.path.join(DATA_DIR, name), encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    mcp.run()
