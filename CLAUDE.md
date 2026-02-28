# CLAUDE.md — poc-mcp

## Contexte du projet

Wrapper Python de l'API Uber Eats basé sur 5 fichiers OpenAPI JSON situés dans `uber_eats_api_doc/`.

**Environnement :**
- Python 3.12+
- Dépendances : `requests`, `pydantic>=2.0`, `dotenv`
- Gestionnaire de packages : `uv` (fichier `uv.lock` présent)

**Variables d'environnement** (fichier `.env`) :
- `UBER_EATS_API_CALLS_DOMAIN` — base URL de l'API (sandbox : `https://test-api.uber.com`)
- `UBER_EATS_AUTHENT_DOMAIN` — domaine d'authentification OAuth
- `UBER_EATS_API_TOKEN` — bearer token actif
- `UBER_EATS_CLIENT_ID` / `UBER_EATS_CLIENT_SECRET` — credentials OAuth

---

## Structure du projet

```
api/
├── __init__.py                  # exporte UberEatsClient, UberEatsAPIError
├── client.py                    # client HTTP de base (session, auth, gestion d'erreurs)
├── models/
│   ├── __init__.py              # exporte tous les modèles
│   ├── common.py                # UberEatsBaseModel, CurrencyAmount, Money, PaginationData
│   ├── stores.py                # Store, StoreList, StoreStatusResponse + enums
│   ├── orders.py                # RestaurantOrder, OrderList, Order, Cart, Item... + enums
│   └── promotions.py            # BasePromotion, FlatOffPromotion, PercentOffPromotion... + parse_promotion()
└── services/
    ├── __init__.py
    ├── stores.py                # StoresService — Store API (7 endpoints)
    ├── orders.py                # OrdersService — Order Fulfillment API (10 endpoints)
    ├── delivery.py              # DeliveryService — Delivery Partner / DMC (1 endpoint)
    ├── byoc.py                  # BYOCService — Bring Your Own Courier (1 endpoint)
    └── promotions.py            # PromotionsService — Promotions API (4 endpoints + helpers)

uber_eats_api_doc/
├── openapi.json                 # Store API
├── openapi (1).json             # Order Fulfillment API
├── openapi (2).json             # Delivery Partner API
├── openapi (3).json             # BYOC Delivery API
└── openapi (4).json             # Promotions API
```

---

## Architecture

### Client (`api/client.py`)

`UberEatsClient` gère :
- La session `requests` avec header `Authorization: Bearer <token>` automatique
- Les méthodes `get()`, `post()`, `delete()` qui retournent des `dict`
- La levée de `UberEatsAPIError` (avec `status_code`, `code`, `message`, `metadata`) pour tout statut HTTP non-2xx
- L'accès lazy aux services via des propriétés : `client.stores`, `client.orders`, `client.delivery`, `client.byoc`, `client.promotions`

```python
from api import UberEatsClient, UberEatsAPIError
client = UberEatsClient()  # lit le .env automatiquement
```

### Modèles (`api/models/`)

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

### Services (`api/services/`)

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
| delivery | `update_partner_count()` | `dict` |
| byoc | `ingest_courier_location()` | `dict` |

**Helpers statiques sur `PromotionsService` :** `flat_off()`, `percent_off()`, `free_delivery()` pour construire les payloads de promotion.

---

## APIs couvertes

| Fichier OpenAPI | API | Base URL |
|-----------------|-----|----------|
| `openapi.json` | Marketplace Store API | `https://api.uber.com` |
| `openapi (1).json` | Order Fulfillment API | `https://api.uber.com` |
| `openapi (2).json` | Delivery Partner API | `https://api.uber.com` |
| `openapi (3).json` | Delivery BYOC API | `https://api.uber.com` |
| `openapi (4).json` | Marketplace Promotions API | `https://api.uber.com` |

**Scopes OAuth :** `eats.store`, `eats.order`, `eats.store.orders.read`, `delivery.multiple.courier`, `eats.byoc.position`, `eats.store.promotion.write`

---

## Patterns à respecter

- Ne pas modifier `UberEatsBaseModel` (extra="ignore" est intentionnel)
- Les nouveaux services doivent suivre le même pattern : importer les modèles au top-level (pas dans `TYPE_CHECKING`), retourner `Model.model_validate(data)`
- Les nouveaux modèles doivent hériter de `UberEatsBaseModel` et avoir tous les champs `Optional`
- `api/models/__init__.py` doit être mis à jour à chaque nouveau modèle
- Le préfixe `Bearer` est ajouté automatiquement dans `client.py` — ne pas l'inclure dans le token du `.env`
