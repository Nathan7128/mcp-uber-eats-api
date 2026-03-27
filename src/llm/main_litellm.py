import asyncio
import os
import sys

import litellm
from dotenv import load_dotenv
from litellm import experimental_mcp_client
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

MODEL = os.getenv("LLM_MODEL", "ollama/llama3.2")

# Chemin absolu vers le module serveur MCP
_env = {**os.environ}
MCP_SERVER_PARAMS = StdioServerParameters(
    command="uv",
    args=["run", "python", "-m", "mcp_server.server"],
    cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")),
    env=_env,
)

SYSTEM_PROMPT = (
    "Tu es un assistant pour restaurateurs utilisant Uber Eats. "
    "Tu as accès à des outils pour consulter les restaurants, commandes et promotions via l'API Uber Eats. "
    "Réponds en français, de manière concise et utile."
)


async def run_agentic_loop(session: ClientSession, messages: list[dict]) -> str:
    """Boucle agentique : appelle le LLM et exécute les tool calls jusqu'à obtenir une réponse finale."""
    tools = await experimental_mcp_client.load_mcp_tools(session=session, format="openai")

    while True:
        response = await litellm.acompletion(
            model=MODEL,
            messages=messages,
            tools=tools,
        )

        message = response.choices[0].message
        finish_reason = response.choices[0].finish_reason

        if finish_reason == "tool_calls" or (message.tool_calls and len(message.tool_calls) > 0):
            messages.append(message.model_dump(exclude_none=True))

            for tool_call in message.tool_calls:
                print(f"  [outil] {tool_call.function.name}({tool_call.function.arguments})")
                result = await experimental_mcp_client.call_openai_tool(
                    session=session,
                    openai_tool=tool_call.model_dump(),
                )
                content = result.content[0].text if result.content else ""
                messages.append({
                    "role": "tool",
                    "content": content,
                    "tool_call_id": tool_call.id,
                })
        else:
            return message.content or ""


async def main() -> None:
    print(f"Connexion au serveur MCP (modèle : {MODEL})...")

    async with stdio_client(MCP_SERVER_PARAMS) as (read, write):
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
                    answer = await run_agentic_loop(session, conversation)
                    print(f"\nAssistant : {answer}\n")
                    conversation.append({"role": "assistant", "content": answer})
                except Exception as e:
                    print(f"\n[Erreur] {e}\n", file=sys.stderr)
                    # On retire le dernier message utilisateur pour ne pas polluer l'historique
                    conversation.pop()


if __name__ == "__main__":
    asyncio.run(main())
