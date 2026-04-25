"""Point d'entrée stdio du serveur MCP.

Même si le serveur sera toujours lancé via le script main.py et connecté au LLM, j'ai considéré l'éventualité
ou le serveur serait lancé à part via une ligne de commande, en parsant les arguments passés dans la ligne de commande.

Usage :
    uv run python -m mcp_server.server              # API réelle
    uv run python -m mcp_server.server --mock       # données synthétiques
    uv run python -m mcp_server.server --transport sse --port 8080
"""

import os
import argparse
from mcp import StdioServerParameters

def build_server_params(project_root: str, use_mock: bool = False):
    args = ["run", "python", "-m", "mcp_server.server"]
    if use_mock:
        args.append("--mock")

    return StdioServerParameters(
        command="uv",
        args=args,
        cwd=project_root,
        env={**os.environ, "USE_MOCK": "true" if use_mock else "false"},
    )


if __name__ == "__main__":
    # Lancement du serveur en se basant sur les arguments spécifiés aux préalable.

    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse", "http"])
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--mock", action="store_true")
    args = parser.parse_args()
    
    if args.mock:
        os.environ["USE_MOCK"] = "true"
    # Import différé du MCP après avoir set la variable d'environnement "USE_MOCK"
    from mcp_server.tools import mcp

    if args.transport == "stdio":
        mcp.run()
    else:
        mcp.run(transport=args.transport, port=args.port, host=args.host)
