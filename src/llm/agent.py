"""Boucle agentique LiteLLM + MCP et construction des paramètres serveur.

`run_agentic_loop` gère le cycle LLM → tool_calls → résultats → LLM
jusqu'à obtenir une réponse textuelle finale (finish_reason != tool_calls).
"""
from typing import Any

import litellm
from litellm import experimental_mcp_client
from mcp import ClientSession


async def run_agentic_loop(session: ClientSession, messages: list[dict[str, Any]], model: str) -> str:
    """Boucle agentic via laquelle l'utilisateur échange avec le LLM, qui interragit avec les tools MCP."""
    
    # Load les tools MCP
    tools = await experimental_mcp_client.load_mcp_tools(session=session, format="openai")

    while True:
        response = await litellm.acompletion(
            model=model,
            messages=messages,
            tools=tools,
        )

        message = response.choices[0].message
        finish_reason = response.choices[0].finish_reason

        if finish_reason == "tool_calls" or message.tool_calls:
            messages.append(message.model_dump(exclude_none=True))

            for tool_call in message.tool_calls:
                print(f"  [tool] {tool_call.function.name}({tool_call.function.arguments})")
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