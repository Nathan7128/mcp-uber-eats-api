# CLAUDE.md — poc-mcp

## Contexte du projet

Wrapper Python de l'API Uber Eats basé sur 5 fichiers OpenAPI JSON situés dans `uber_eats_api_doc/`.

**Environnement :**
- Python 3.12+
- Dépendances : `requests`, `pydantic>=2.0`, `python-dotenv>=1.0.0`, `fastapi>=0.115.0`, `uvicorn[standard]>=0.30.0`
- Gestionnaire de packages : `uv` (fichier `uv.lock` présent)
- Binaire uv installé dans `~/.local/bin/uv` (à ajouter au PATH si absent)

**Démarrage du serveur FastAPI :**
```bash
uv run uvicorn app.main:app --reload
# Swagger UI disponible sur http://localhost:8000/docs
```

**Variables d'environnement** (fichier `.env`) :
- `UBER_EATS_API_CALLS_DOMAIN` — base URL de l'API (sandbox : `https://test-api.uber.com`)
- `UBER_EATS_AUTHENT_DOMAIN` — domaine d'authentification OAuth
- `UBER_EATS_API_TOKEN` — bearer token actif
- `UBER_EATS_CLIENT_ID` / `UBER_EATS_CLIENT_SECRET` — credentials OAuth

---

## Structure du projet

```
app/
├── __init__.py          # exporte UberEatsClient, UberEatsAPIError
├── client.py            # client HTTP de base (session, auth, gestion d'erreurs)
├── main.py              # FastAPI entry point — montage des routers + exception handler UberEatsAPIError
├── dependencies.py      # get_client() — singleton UberEatsClient via lru_cache
├── models/
│   ├── __init__.py      # exporte tous les modèles
│   ├── common.py        # UberEatsBaseModel, CurrencyAmount, Money, PaginationData
│   ├── stores.py        # Store, StoreList, StoreStatusResponse + enums
│   ├── orders.py        # RestaurantOrder, OrderList, Order, Cart, Item... + enums
│   └── promotions.py   # BasePromotion, FlatOffPromotion, PercentOffPromotion... + parse_promotion()
├── routers/
│   ├── __init__.py
│   ├── stores.py        # GET /stores, GET /stores/{id}, GET /stores/{id}/status
│   ├── orders.py        # GET /orders/{id}, GET /stores/{id}/orders
│   └── promotions.py   # GET /promotions/{id}, GET /stores/{id}/promotions
└── services/
    ├── __init__.py
    ├── stores.py        # StoresService — Store API (7 endpoints)
    ├── orders.py        # OrdersService — Order Fulfillment API (10 endpoints)
    └── promotions.py   # PromotionsService — Promotions API (4 endpoints + helpers)

uber_eats_api_doc/
├── openapi.json                 # Store API
├── openapi (1).json             # Order Fulfillment API
└── openapi (4).json             # Promotions API
```

---

## Architecture

### Client (`app/client.py`)

`UberEatsClient` gère :
- La session `requests` avec header `Authorization: Bearer <token>` automatique
- Les méthodes `get()`, `post()`, `delete()` qui retournent des `dict`
- La levée de `UberEatsAPIError` (avec `status_code`, `code`, `message`, `metadata`) pour tout statut HTTP non-2xx
- L'accès lazy aux services via des propriétés : `client.stores`, `client.orders`, `client.promotions`

```python
from app import UberEatsClient, UberEatsAPIError
client = UberEatsClient()  # lit le .env automatiquement
```

### Modèles (`app/models/`)

Tous les modèles héritent de `UberEatsBaseModel` (Pydantic v2) :
- `extra="ignore"` — champs inconnus de l'API silencieusement ignorés
- `populate_by_name=True` — population par nom de champ
- Tous les champs sont `Optional` avec défaut `None`

**Conventions monétaires :** `CurrencyAmount.amount_e5` est l'unité interne Uber (×10⁵). La propriété `.amount` retourne le décimal lisible.

**Promotions — pattern factory :** `parse_promotion(data: dict) -> BasePromotion` retourne le bon sous-type en fonction de `promo_type`. Utilisé automatiquement par `PromotionsService.get()` et `PromotionList`.

**Raccourcis utiles sur les modèles :**
- `StoreStatusResponse.is_online` → bool
- `OrderList.orders` → `List[Order]` (dépaquète les wrappers `RestaurantOrder`)
- `Order.primary_customer` → `Customer | None`
- `Order.item_count` → int

### Services (`app/services/`)

Chaque service reçoit le `client` en constructeur et appelle `Model.model_validate(data)` sur les réponses.

**Retours typés :**
| Service | Méthode | Retour |
|---------|---------|--------|
| stores | `list()` | `StoreList` |
| stores | `get()`, `update()`, `update_status()` | `Store` |
| stores | `get_status()` | `StoreStatusResponse` |
| stores | `update_prep_time()`, `update_fulfillment_config()` | `dict` |
| orders | `get()` | `RestaurantOrder` |
| orders | `list()` | `OrderList` |
| orders | `adjust_price()` | `AdjustPriceResponse` |
| orders | autres actions (accept, deny, cancel…) | `dict` |
| promotions | `create()` | `CreatePromotionResponse` |
| promotions | `get()` | `BasePromotion` (sous-type selon `promo_type`) |
| promotions | `list()` | `PromotionList` |
| promotions | `revoke()` | `dict` |

**Helpers statiques sur `PromotionsService` :** `flat_off()`, `percent_off()`, `free_delivery()` pour construire les payloads de promotion.

---

## APIs couvertes

| Fichier OpenAPI | API | Base URL |
|-----------------|-----|----------|
| `openapi.json` | Marketplace Store API | `https://api.uber.com` |
| `openapi (1).json` | Order Fulfillment API | `https://api.uber.com` |
| `openapi (4).json` | Marketplace Promotions API | `https://api.uber.com` |

**Scopes OAuth :** `eats.store`, `eats.order`, `eats.store.orders.read`, `eats.store.promotion.write`

---

## Couche FastAPI (`app/`)

### Architecture
- `app/dependencies.py` — `get_client()` retourne un singleton `UberEatsClient` via `@lru_cache`. À injecter avec `Depends(get_client)` dans chaque endpoint.
- `app/main.py` — crée l'app FastAPI, enregistre un `exception_handler` pour `UberEatsAPIError` (mappe sur `JSONResponse` avec le `status_code` Uber), inclut les 3 routers.
- Les modèles `app/models/` sont réutilisés directement comme `response_model` FastAPI (Pydantic v2 compatible).

### Endpoints exposés (GET uniquement)
| Méthode | Path | Service | response_model |
|---------|------|---------|---------------|
| GET | `/stores` | `stores.list()` | `StoreList` |
| GET | `/stores/{store_id}` | `stores.get()` | `Store` |
| GET | `/stores/{store_id}/status` | `stores.get_status()` | `StoreStatusResponse` |
| GET | `/orders/{order_id}` | `orders.get()` | `RestaurantOrder` |
| GET | `/stores/{store_id}/orders` | `orders.list()` | `OrderList` |
| GET | `/promotions/{promotion_id}` | `promotions.get()` | `BasePromotion` |
| GET | `/stores/{store_id}/promotions` | `promotions.list()` | `PromotionList` |

### Conventions routers
- Chaque endpoint a une `description` orientée action (pour futur MCP)
- `Path(description=...)` sur les path params, `Query(description=...)` sur les query params
- Les valeurs possibles des enums sont documentées dans la description du paramètre

---

## Patterns à respecter

- Ne pas modifier `UberEatsBaseModel` (extra="ignore" est intentionnel)
- Les nouveaux services doivent suivre le même pattern : importer les modèles au top-level (pas dans `TYPE_CHECKING`), retourner `Model.model_validate(data)`
- Les nouveaux modèles doivent hériter de `UberEatsBaseModel` et avoir tous les champs `Optional`
- `app/models/__init__.py` doit être mis à jour à chaque nouveau modèle
- Le préfixe `Bearer` est ajouté automatiquement dans `client.py` — ne pas l'inclure dans le token du `.env`
- Les nouveaux endpoints FastAPI (GET) suivent le pattern : `Depends(get_client)` + `response_model` explicite + descriptions détaillées
