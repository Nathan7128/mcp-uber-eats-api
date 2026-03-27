# mcp-uber-eats-api

Serveur [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) exposant des outils de lecture de l'API Uber Eats, destiné à être intégré dans des plateformes de chatbots ou des pipelines RAG pour restaurateurs.

Construit avec [FastMCP](https://github.com/jlowin/fastmcp), [Pydantic v2](https://docs.pydantic.dev/) et Python 3.12+.

---

## Outils MCP disponibles

| Outil | Description |
|-------|-------------|
| `list_stores` | Liste tous les restaurants du compte |
| `get_store` | Détails d'un restaurant (horaires, adresse, configuration) |
| `get_store_status` | Statut en ligne / hors ligne d'un restaurant |
| `get_order` | Détails complets d'une commande (articles, client, statut) |
| `list_store_orders` | Commandes d'un restaurant, filtrables par statut ou période |
| `get_promotion` | Détails d'une promotion spécifique |
| `list_store_promotions` | Promotions actives d'un restaurant |

---

## Installation

**Prérequis :** Python 3.12+, [`uv`](https://docs.astral.sh/uv/), un token Uber Eats API.

```bash
git clone https://github.com/Nathan7128/mcp-uber-eats-api
cd mcp-uber-eats-api
cp .env.example .env   # puis renseigner les variables
uv sync
```

### Variables d'environnement (`.env`)

| Variable | Description | Requis |
|----------|-------------|--------|
| `UBER_EATS_API_TOKEN` | Bearer token Uber Eats | Oui |
| `UBER_EATS_API_CALLS_DOMAIN` | Base URL de l'API (défaut : `https://api.uber.com`) | Non |
| `MOCK_API` | Mettre à `1` pour utiliser les fixtures de test | Non |
| `GEMINI_API_KEY` | Clé Google AI Studio (boucle LiteLLM uniquement) | Non |
| `LLM_MODEL` | Modèle LiteLLM (défaut : `gemini/gemini-2.5-flash`) | Non |

---

## Utilisation

```bash
# Démarrer le serveur MCP (transport stdio, mode production)
uv run python -m mcp_server.server

# Interface de debug FastMCP (navigateur)
uv run fastmcp dev src/mcp_server/tools.py

# Boucle de conversation interactive LLM + MCP
uv run python -m llm.main_litellm
```

---

## Intégration dans un client MCP

Exemple de configuration pour Claude Desktop (`claude_desktop_config.json`) :

```json
{
  "mcpServers": {
    "uber-eats": {
      "command": "uv",
      "args": ["run", "python", "-m", "mcp_server.server"],
      "cwd": "/chemin/vers/mcp-uber-eats-api",
      "env": {
        "UBER_EATS_API_TOKEN": "...",
        "UBER_EATS_API_CALLS_DOMAIN": "https://api.uber.com"
      }
    }
  }
}
```

---

## Tests

```bash
uv run pytest                  # suite complète (125 tests)
MOCK_API=1 uv run pytest       # sans credentials réels
```

---

## Architecture

```
src/
  mcp_server/
    client.py       # Client HTTP (auth, timeout, gestion d'erreurs)
    tools.py        # 7 outils FastMCP — entry point de la logique métier
    server.py       # Entry point CLI (stdio / SSE / HTTP)
    mock_client.py  # Client mock basé sur des fixtures (MOCK_API=1)
    models/
      stores.py     # StoreModel, StoreStatusModel, StoreListModel
      orders.py     # OrderModel, OrderListModel
      promotions.py # PromotionModel, PromotionListModel
  llm/
    main_litellm.py # Boucle REPL interactive (LiteLLM + MCP)
tests/
  fixtures.py       # Données de test réalistes (5 restaurants)
  test_models.py    # Tests unitaires des modèles Pydantic
  test_tools.py     # Tests d'intégration des outils MCP
```

Les modèles Pydantic filtrent et aplatissent les réponses brutes de l'API pour ne retourner que les champs pertinents au LLM.
