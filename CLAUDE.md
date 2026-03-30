# CLAUDE.md — poc-mcp

## Contexte du projet

Serveur MCP Python exposant des outils de lecture de l'API Uber Eats, destiné à être intégré dans une plateforme de chatbots/RAG utilisée par des restaurateurs.

**Environnement :**
- Python 3.12+
- Dépendances : `fastmcp>=3.1.0`, `requests>=2.32.5`, `pydantic>=2.0.0`, `python-dotenv>=1.0.0`, `litellm>=1.82.6`, `mcp>=1.0.0`
- Gestionnaire de packages : `uv` (fichier `uv.lock` présent)
- Binaire uv installé dans `~/.local/bin/uv` (à ajouter au PATH si absent)

**Démarrage du serveur MCP :**
```bash
uv run python -m mcp_server.server              # transport stdio (production, API réelle)
uv run python -m mcp_server.server --mock       # transport stdio avec données synthétiques
uv run fastmcp dev mcp_server/tools.py          # interface de debug FastMCP
```

**Variables d'environnement** (fichier `.env`) :
- `UBER_EATS_API_CALLS_DOMAIN` — base URL de l'API (sandbox : `https://test-api.uber.com`, prod : `https://api.uber.com`)
- `UBER_EATS_API_TOKEN` — bearer token actif
- `UBER_EATS_CLIENT_ID` / `UBER_EATS_CLIENT_SECRET` — credentials OAuth
- `UBER_EATS_AUTHENT_DOMAIN` — domaine d'authentification OAuth

---

## Structure du projet

```
mcp_server/
├── __init__.py
├── client.py         # client HTTP de base (session, auth, gestion d'erreurs)
├── tools.py          # 7 outils MCP — entry point de la logique métier
├── server.py         # entry point stdio : uv run python -m mcp_server.server
└── models/
    ├── __init__.py   # re-exporte tous les modèles
    ├── stores.py     # StoreModel, StoreStatusModel, StoreListModel
    ├── orders.py     # OrderItemModel, OrderModel, OrderListModel
    └── promotions.py # PromotionModel, PromotionListModel

uber_eats_api_doc/
├── openapi.json         # Store API
├── openapi (1).json     # Order Fulfillment API
└── openapi (4).json     # Promotions API
```

---

## Architecture

### Client (`mcp_server/client.py`)

`UberEatsClient` gère :
- La session `requests` avec header `Authorization: Bearer <token>` automatique
- Les méthodes `get()`, `post()`, `delete()` qui retournent des `dict`
- La levée de `UberEatsAPIError` (avec `status_code`, `code`, `message`, `metadata`) pour tout statut HTTP non-2xx

```python
from mcp_server.client import UberEatsClient, UberEatsAPIError
client = UberEatsClient()  # lit le .env automatiquement
data = client.get("/v1/delivery/stores")
```

Le préfixe `Bearer` est ajouté automatiquement — ne pas l'inclure dans le token du `.env`.

### Modèles (`mcp_server/models/`)

Rôle : recevoir la réponse brute de l'API Uber Eats, filtrer les champs pertinents pour le LLM, et retourner un dict propre via `.model_dump(exclude_none=True)`.

Tous les modèles héritent de `BaseModel` (Pydantic v2) avec `ConfigDict(extra="ignore")` — le bruit de l'API est automatiquement supprimé. Tous les champs sont `Optional` avec défaut `None`.

Les `@model_validator(mode="before")` sont utilisés pour aplatir les structures imbriquées de l'API :
- `StoreModel` : extrait `address` depuis `location`, `prep_time_seconds` depuis `prep_times.default_value`, `merchant_type` depuis `uber_merchant_type.type`
- `StoreStatusModel` : calcule `is_online` (bool), renomme `reason` → `offline_reason`, `is_offline_until` → `offline_until`
- `StoreListModel` : mappe `data` → `stores`, extrait `next_page_token` depuis `pagination_data`
- `OrderModel` : extrait `customer_name` et `customer_phone` depuis `customers[]`, aplatit `carts[].items[]` → `items`, calcule `item_count`, extrait `delivery_status` depuis `deliveries[0].status`
- `OrderListModel` : dépaquète les wrappers `{"order": {...}}` dans `data[]`, extrait `next_page_token` et `total_count`
- `PromotionModel` : mappe `promo_type` → `type`, extrait `target_customers` depuis `promotion_customization.user_group`, place le bon sous-objet de discount dans `discount_details`

### Server (`mcp_server/server.py`)

Entry point stdio. L'import de `tools.py` est **différé** (à l'intérieur du `if __name__ == "__main__"`) afin que la variable `MOCK_API` soit injectée dans l'environnement avant que `tools.py` ne la lise.

Flag `--mock` : si présent, positionne `os.environ["MOCK_API"] = "1"` avant l'import de `tools`.

### Tools (`mcp_server/tools.py`)

7 outils MCP enregistrés sur un `FastMCP(name="UberEatsAPIWrapper")`. Chaque outil :
1. Appelle `client.get(path, params)` directement (pas de couche service)
2. Parse avec le modèle : `Model.model_validate(data)`
3. Retourne `.model_dump(exclude_none=True)`

| Outil MCP | Endpoint API | Modèle |
|-----------|-------------|--------|
| `list_stores` | `GET /v1/delivery/stores` | `StoreListModel` |
| `get_store` | `GET /v1/delivery/store/{store_id}` | `StoreModel` |
| `get_store_status` | `GET /v1/delivery/store/{store_id}/status` | `StoreStatusModel` |
| `get_order` | `GET /v1/delivery/order/{order_id}` | `OrderModel` |
| `list_store_orders` | `GET /v1/delivery/store/{store_id}/orders` | `OrderListModel` |
| `get_promotion` | `GET /v1/delivery/promotions/{promotion_id}` | `PromotionModel` |
| `list_store_promotions` | `GET /v1/delivery/stores/{store_id}/promotions` | `PromotionListModel` |

**Note :** `get_order` dépaquète le wrapper `{"order": {...}}` avant de valider : `data.get("order", data)`.

---

## APIs couvertes

| Fichier OpenAPI | API | Base URL |
|-----------------|-----|----------|
| `openapi.json` | Marketplace Store API | `https://api.uber.com` |
| `openapi (1).json` | Order Fulfillment API | `https://api.uber.com` |
| `openapi (4).json` | Marketplace Promotions API | `https://api.uber.com` |

**Scopes OAuth :** `eats.store`, `eats.order`, `eats.store.orders.read`, `eats.store.promotion.write`

---

## Intégration plateforme chatbot

Transport **stdio**. Configuration côté plateforme :

```json
{
  "mcpServers": {
    "uber-eats": {
      "command": "uv",
      "args": ["run", "python", "-m", "mcp_server.server"],
      "cwd": "/path/to/wrapper-uber-eats-api",
      "env": {
        "UBER_EATS_API_TOKEN": "...",
        "UBER_EATS_API_CALLS_DOMAIN": "https://api.uber.com"
      }
    }
  }
}
```

---

## Stack LiteLLM (`src/llm/`)

Module de test interactif du LLM connecté au serveur MCP, en boucle de conversation dans le terminal.

**Démarrage :**
```bash
uv run python main.py
```

**Variables d'environnement** supplémentaires (fichier `.env`) :
- `LLM_MODEL` — modèle LiteLLM à utiliser (défaut : `ollama/llama3.2`)
- `OLLAMA_MODEL` — nom du modèle Ollama à télécharger (défaut : `llama3.2`)
- `OLLAMA_API_BASE` — URL du serveur Ollama (défaut local : `http://localhost:11434`, devcontainer : `http://ollama:11434`)

**Fonctionnement :**
1. Demande à l'utilisateur s'il souhaite utiliser les données mock ou l'API réelle
2. Lance le serveur MCP en subprocess via `stdio_client` (avec `--mock` si mock choisi)
3. Charge les outils MCP au démarrage via `experimental_mcp_client.load_mcp_tools`
4. Boucle de conversation : lit un prompt → boucle agentique → affiche la réponse
5. La boucle agentique gère les `tool_calls` : exécute chaque outil MCP et renvoie le résultat au LLM jusqu'à obtenir une réponse textuelle finale

**Structure :**
```
main.py               # entry point CLI : boucle REPL + config (MODEL, SYSTEM_PROMPT)
llm/
├── __init__.py       # re-exporte run_agentic_loop, build_server_params
└── agent.py          # boucle agentique LiteLLM+MCP + construction des params serveur
```

**Packaging :** `hatchling` est utilisé comme build backend (`pyproject.toml`) pour exposer `src/mcp_server` et `src/llm` comme packages Python installables depuis la racine du projet.

---

## Patterns à respecter

- Pas de couche services — les tools appellent `client.get()` directement
- Les nouveaux modèles héritent de `BaseModel` avec `ConfigDict(extra="ignore")`, tous les champs `Optional`
- `mcp_server/models/__init__.py` doit être mis à jour à chaque nouveau modèle
- Les nouveaux tools suivent le pattern : `client.get()` → `Model.model_validate(data)` → `.model_dump(exclude_none=True)`
- Les descriptions des tools sont orientées restaurateur (pas technique)
