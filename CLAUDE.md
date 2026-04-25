# CLAUDE.md — mcp-uber-eats-api

Parle-moi toujours en français.

## Contexte du projet

Chatbot agentic combinant un serveur **MCP** (FastMCP) qui expose les endpoints de l'API **Uber Eats Marketplace** sous forme d'outils, et une boucle agentic **LiteLLM** qui les utilise pour répondre aux prompts utilisateur.

- **Cible** : restaurateurs / commerçants disposant d'une API key Uber Eats.
- **Orchestration** : tout passe par `main.py` (REPL conversationnel).
- **Mode mock** : un client simulé avec données synthétiques (`src/mcp_server/mocks/`) permet de tester sans API réelle.

## Environnement

- **Python** 3.12+ (cf. `.python-version`)
- **Gestionnaire de packages** : `uv` (lock file `uv.lock` présent ; binaire dans `~/.local/bin/uv`)
- **Dépendances clés** (cf. `pyproject.toml`) : `fastmcp>=2.2.0`, `litellm>=1.83.10`, `mcp>=1.27.0`, `dotenv>=0.9.9`
- **Devcontainer** disponible dans `.devcontainer/` (avec `setup.sh` d'init)

## Variables d'environnement (`.env`)

LLM :
- `LLM_MODEL` — modèle utilisé par LiteLLM (défaut : `groq/llama-3.3-70b-versatile`)
- `GROQ_API_KEY` — clé API du provider (à adapter selon le LLM choisi)

Uber Eats — utilisées :
- `UBER_EATS_API_CALLS_DOMAIN` — base URL (sandbox : `https://test-api.uber.com`, prod : `https://api.uber.com`)
- `UBER_EATS_API_TOKEN` — Bearer token actif

Uber Eats — **présentes mais non utilisées actuellement** (réservées à un futur flux OAuth) :
- `UBER_EATS_CLIENT_ID`, `UBER_EATS_CLIENT_SECRET`, `UBER_EATS_AUTHENT_DOMAIN`

Runtime interne (pas dans `.env`) :
- `USE_MOCK` — défini par `main.py` ou `server.py` avant l'import de `tools.py` pour basculer entre client réel et mock.

## Démarrage

Flux principal (chatbot) :
```bash
uv run python main.py    # REPL ; demande mock ou prod au lancement
./start.sh               # idem, avec vérification des prérequis
```

Lancement direct du serveur MCP (utile pour usage hors-chatbot, debug ou intégration tierce ; pas le flux principal) :
```bash
uv run python -m mcp_server.server [--mock] [--transport stdio|sse|http] [--port N]
uv run fastmcp dev src/mcp_server/tools.py    # interface de debug FastMCP
```

## Structure du projet

Le code source est dans `src/`. Le point d'entrée `main.py` est à la racine.

**`main.py`** — Charge `.env`, demande à l'utilisateur le mode (mock / prod), lance le serveur MCP en sous-processus stdio via `build_server_params`, et exécute la boucle conversationnelle via `run_agentic_loop`.

### `src/mcp_server/`

- **`server.py`** — Expose `build_server_params(project_root, use_mock)` qui construit les `StdioServerParameters`. Set `USE_MOCK` *avant* d'importer `tools.py` (ordre critique).
- **`tools.py`** — Instancie `FastMCP` et expose 7 outils :
  - `list_stores`, `get_store`, `get_store_status`
  - `list_store_orders`, `get_order`
  - `list_store_promotions`, `get_promotion`

  Le client utilisé (`UberEatsClient` ou `MockUberEatsClient`) est sélectionné à l'import en lisant `os.getenv("USE_MOCK")`.
- **`client.py`** — `UberEatsClient` (session `requests` + Bearer token, méthodes `get` / `post` / `delete`) et `UberEatsAPIError` (exception structurée parsant le JSON d'erreur Uber Eats).
- **`models/`** — Modèles Pydantic v2 : `orders.py`, `stores.py`, `promotions.py`. Tous utilisent `@model_validator(mode="before")` pour aplatir / remapper la structure imbriquée renvoyée par l'API (ex : `customers[]` → champs racine, `carts[].items[]` → liste plate, `selected_modifier_groups` → modifieurs simplifiés). Configurés en `extra="ignore"`.
- **`mocks/`** — `MockUberEatsClient` (regex routing, `copy.deepcopy` à chaque appel pour éviter les mutations partagées) + `fixtures.py` (5 restaurants français, ~15 commandes, ~8 promotions). Seul `get` est implémenté.

### `src/llm/`

- **`agent.py`** — `run_agentic_loop(session, messages, model)` (async). Charge les tools MCP via `litellm.experimental_mcp_client.load_mcp_tools`, appelle `litellm.acompletion`, et boucle tant que `finish_reason == "tool_calls"` en exécutant chaque appel via `experimental_mcp_client.call_openai_tool` puis en réinjectant le résultat dans `messages`. Log `[tool] nom(args)` à chaque appel.

## Patterns clés

- **Sélection client au runtime** : `tools.py` lit `USE_MOCK` à l'import → toujours définir cette variable *avant* d'importer le module, sinon c'est le client réel qui sera instancié.
- **Validation → dump** : chaque outil MCP retourne `Model.model_validate(data).model_dump(exclude_none=True)` pour livrer au LLM une structure plate et sans champs vides.
- **Async partout** : `main.py` utilise `asyncio.run` ; `agent.py` est entièrement async (acompletion + session MCP).

## Pièges connus

- `USE_MOCK` doit impérativement être défini *avant* l'import de `tools.py`.
- Aucun retry ni gestion silencieuse d'erreurs côté `UberEatsClient` — un token invalide lève `UberEatsAPIError`.
- L'historique des messages s'accumule sans cap dans `main.py` : coûteux en tokens sur longues conversations.
- `MockUberEatsClient` n'implémente que `get` (pas `post` / `delete`) ; tout outil futur en écriture devra étendre le mock.

## Tests

Aucun test automatisé à ce jour. Validation manuelle via le mode mock (prompts type : « Quels sont mes restaurants ? », « Liste les commandes ACCEPTED du Bistro du Coin »).
