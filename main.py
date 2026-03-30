"""Interface REPL en ligne de commande pour tester le LLM connecté au serveur MCP.

Lance le serveur MCP en subprocess (stdio), charge les outils, puis démarre
une boucle de conversation interactive dans le terminal.
"""
import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from mcp.client.stdio import stdio_client
from mcp import ClientSession

from llm import build_server_params, run_agentic_loop

load_dotenv()

MODEL = os.getenv("LLM_MODEL")
PROJECT_ROOT = str(Path(__file__).parent)

SYSTEM_PROMPT = (
    "Tu es un assistant pour restaurateurs utilisant Uber Eats. "
    "Tu as accès à des outils pour consulter les restaurants, commandes et promotions via l'API Uber Eats. "
    "Réponds en français, de manière concise et utile."
)


async def main() -> None:
    use_mock = input("Utiliser les données de test (mock) ? [o/N] : ").strip().lower() in {"o", "oui", "y", "yes"}
    mode = "mock" if use_mock else "API réelle"
    print(f"Connexion au serveur MCP (modèle : {MODEL}, données : {mode})...")

    params = build_server_params(use_mock, PROJECT_ROOT)

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("Serveur MCP connecté. Tapez 'quit' ou 'exit' pour quitter.\n")

            conversation: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

            while True:
                try:
                    user_input = input("Vous : ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\nAu revoir !")
                    break

                if not user_input:
                    continue
                if user_input.lower() in {"quit", "exit", "q"}:
                    print("Au revoir !")
                    break

                conversation.append({"role": "user", "content": user_input})

                try:
                    answer = await run_agentic_loop(session, conversation, MODEL)
                    print(f"\nAssistant : {answer}\n")
                    conversation.append({"role": "assistant", "content": answer})
                except Exception as e:
                    print(f"\n[Erreur] {e}\n", file=sys.stderr)
                    conversation.pop()


if __name__ == "__main__":
    asyncio.run(main())
