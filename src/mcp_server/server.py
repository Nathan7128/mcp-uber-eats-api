"""Entry point for the Uber Eats MCP server.

Run with:
    uv run python -m mcp_server.server                              # stdio (default)
    uv run python -m mcp_server.server --transport sse              # SSE
    uv run python -m mcp_server.server --transport http --port 8080 # HTTP
"""
from mcp_server.tools import mcp

if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse", "http"])
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", default="0.0.0.0")
    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run()
    else:
        mcp.run(transport=args.transport, port=args.port, host=args.host)
