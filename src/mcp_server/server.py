"""Point d'entrée stdio du serveur MCP.

Usage :
    uv run python -m mcp_server.server              # API réelle
    uv run python -m mcp_server.server --mock       # données synthétiques
    uv run python -m mcp_server.server --transport sse --port 8080
"""
if __name__ == "__main__":
    import sys
    import os
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse", "http"])
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--mock", action="store_true", help="Use synthetic mock data instead of the real API")
    args = parser.parse_args()

    if args.mock:
        os.environ["MOCK_API"] = "1"

    from mcp_server.tools import mcp  # Deferred import so MOCK_API is set in env before tools.py reads it

    if args.transport == "stdio":
        mcp.run()
    else:
        mcp.run(transport=args.transport, port=args.port, host=args.host)
