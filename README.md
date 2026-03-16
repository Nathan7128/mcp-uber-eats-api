# wrapper-uber-eats-api

Wrapper Python de l'API Uber Eats Marketplace permettant d'accéder aux différents endpoints disponibles et de récupérer les données sous forme d'objets Pydantic typés.

Le projet inclut également un client mock et des fixtures de données synthétiques pour tester le wrapper sans credentials réels.

## Fonctionnalités

- **5 APIs couvertes** : Store, Order Fulfillment, Delivery Partner, BYOC, Promotions
- **23 endpoints** accessibles via des méthodes Python idiomatiques
- **Modèles Pydantic v2** : toutes les réponses sont désérialisées en objets typés
- **Gestion d'erreurs** : `UberEatsAPIError` avec `status_code`, `code`, `message` et `metadata`
- **Client mock** : tests sans appels réseau grâce à `MockUberEatsClient`
- **Helpers de promotion** : méthodes statiques pour construire les payloads

## Prérequis

- Python 3.12+
- [`uv`](https://github.com/astral-sh/uv) (gestionnaire de packages recommandé)

## Installation

```bash
git clone <url-du-repo>
cd wrapper-uber-eats-api
uv sync
```

## Configuration

Créez un fichier `.env` à la racine du projet :

```env
UBER_EATS_API_CALLS_DOMAIN=https://test-api.uber.com   # sandbox
UBER_EATS_AUTHENT_DOMAIN=https://login.uber.com
UBER_EATS_API_TOKEN=your_bearer_token_here
UBER_EATS_CLIENT_ID=your_client_id
UBER_EATS_CLIENT_SECRET=your_client_secret
```

> Le préfixe `Bearer` est ajouté automatiquement — ne pas l'inclure dans le token.

## Utilisation

### Initialisation du client

```python
from api import UberEatsClient, UberEatsAPIError

client = UberEatsClient()  # lit le .env automatiquement
```

### Stores

```python
# Lister tous les restaurants
stores = client.stores.list()
for store in stores.data:
    print(store.id, store.name)

# Détail d'un restaurant
store = client.stores.get("store-uuid")
print(store.location.city)

# Statut en ligne / hors ligne
status = client.stores.get_status("store-uuid")
if status.is_online:
    print("Le restaurant est en ligne")

# Mettre hors ligne
client.stores.update_status("store-uuid", "OFFLINE", reason="STORE_CLOSED")

# Modifier le temps de préparation (en minutes)
client.stores.update_prep_time("store-uuid", original_prep_time=20, updated_prep_time=30)
```

### Commandes

```python
# Récupérer une commande
order_wrapper = client.orders.get("order-uuid")
order = order_wrapper.order
print(order.display_id, order.state)

# Client principal
customer = order.primary_customer
print(str(customer.name))  # "Jean Dupont"

# Nombre total d'articles (somme des quantités)
print(order.item_count)

# Lister les commandes d'un restaurant
order_list = client.orders.list(
    store_id="store-uuid",
    state="OFFERED",      # OFFERED | ACCEPTED | HANDED_OFF | SUCCEEDED | FAILED
    status="ACTIVE",      # SCHEDULED | ACTIVE | COMPLETED
    page_size=20,
)
for order in order_list.orders:  # liste plate de Order (sans wrapper)
    print(order.id, order.state)

# Accepter une commande
client.orders.accept("order-uuid", ready_for_pickup_time="2024-01-15T12:30:00Z")

# Refuser / annuler
client.orders.deny("order-uuid", reason="ITEM_UNAVAILABLE")
client.orders.cancel("order-uuid", reason="KITCHEN_CLOSED")

# Marquer comme prête pour le livreur
client.orders.mark_ready("order-uuid")
```

### Promotions

```python
from api.services.promotions import PromotionsService

# Promotion -3 € dès 15 € d'achat
payload = PromotionsService.flat_off(
    start_time="2024-01-01T00:00:00Z",
    end_time="2024-01-31T23:59:59Z",
    discount_amount=300,   # 3,00 € en centimes
    min_spend=1500,        # panier minimum 15,00 €
    currency_code="EUR",
)
response = client.promotions.create("store-uuid", payload)
print(response.promotion_id)

# Promotion -20 % avec plafond
payload = PromotionsService.percent_off(
    start_time="2024-01-01T00:00:00Z",
    end_time="2024-01-31T23:59:59Z",
    percent_value=20,
    max_discount=500,  # plafond à 5,00 €
    currency_code="EUR",
)

# Livraison offerte
payload = PromotionsService.free_delivery(
    start_time="2024-01-01T00:00:00Z",
    end_time="2024-01-31T23:59:59Z",
)

# Lister les promotions actives d'un restaurant
promo_list = client.promotions.list("store-uuid")
for promo in promo_list.promotions:  # objets typés selon promo_type
    print(promo.promotion_id, promo.promo_type)

# Récupérer une promotion par ID (retourne le sous-type approprié)
promo = client.promotions.get("promo-uuid")  # FlatOffPromotion, PercentOffPromotion, etc.

# Révoquer une promotion
client.promotions.revoke("promo-uuid")
```

### Gestion des erreurs

```python
from api import UberEatsAPIError

try:
    store = client.stores.get("invalid-id")
except UberEatsAPIError as e:
    print(e.status_code)  # ex: 404
    print(e.code)         # ex: "store_not_found"
    print(e.message)
    print(e.metadata)
```

## Tests

Le projet inclut un `MockUberEatsClient` qui simule les appels API avec des fixtures prédéfinies, sans nécessiter de credentials réels.

```bash
# Avec uv (recommandé)
uv run python -m pytest tests/ -v

# Avec pytest directement
python -m pytest tests/ -v

# Avec unittest (stdlib uniquement)
python -m unittest discover tests/
```

### Architecture de test

| Fichier | Rôle |
|---------|------|
| `tests/fixtures.py` | Fausses réponses API (restaurants, commandes, promotions) |
| `tests/mock_client.py` | `MockUberEatsClient` — routeur regex, aucun appel réseau |
| `tests/test_services.py` | Suite de tests unitaires (~40 tests) |

Le `MockUberEatsClient` hérite de `UberEatsClient` et surcharge uniquement les méthodes HTTP bas-niveau (`get`, `post`, `delete`). Tous les service accessors (`.stores`, `.orders`, etc.) fonctionnent à l'identique.

```python
from tests.mock_client import MockUberEatsClient

client = MockUberEatsClient()
stores = client.stores.list()         # retourne StoreList mockée
order = client.orders.get("any-id")  # retourne RestaurantOrder mocké
```

## Structure du projet

```
api/
├── __init__.py                  # exporte UberEatsClient, UberEatsAPIError
├── client.py                    # client HTTP (session, auth, gestion d'erreurs)
├── models/
│   ├── common.py                # UberEatsBaseModel, CurrencyAmount, Money, PaginationData
│   ├── stores.py                # Store, StoreList, StoreStatusResponse + enums
│   ├── orders.py                # RestaurantOrder, OrderList, Order, Cart, Item... + enums
│   └── promotions.py            # BasePromotion, FlatOffPromotion, PercentOffPromotion... + parse_promotion()
└── services/
    ├── stores.py                # StoresService — 7 endpoints
    ├── orders.py                # OrdersService — 10 endpoints
    ├── delivery.py              # DeliveryService — Delivery Partner / DMC
    ├── byoc.py                  # BYOCService — Bring Your Own Courier
    └── promotions.py            # PromotionsService — 4 endpoints + helpers

tests/
├── fixtures.py                  # Données synthétiques (restaurants, commandes, promotions)
├── mock_client.py               # Client HTTP simulé sans appels réseau
└── test_services.py             # Tests unitaires

uber_eats_api_doc/               # Spécifications OpenAPI (5 fichiers JSON)
```

## APIs couvertes

| API | Service | Endpoints | Scopes OAuth requis |
|-----|---------|-----------|---------------------|
| Marketplace Store API | `client.stores` | 7 | `eats.store` |
| Order Fulfillment API | `client.orders` | 10 | `eats.order`, `eats.store.orders.read` |
| Delivery Partner API | `client.delivery` | 1 | `delivery.multiple.courier` |
| BYOC Delivery API | `client.byoc` | 1 | `eats.byoc.position` |
| Marketplace Promotions API | `client.promotions` | 4 | `eats.store.promotion.write` |

## Référence des modèles

### Raccourcis utiles

```python
status.is_online        # bool — statut en ligne d'un restaurant
order_list.orders       # List[Order] — dépaquète les wrappers RestaurantOrder
order.primary_customer  # Customer | None — client principal d'une commande
order.item_count        # int — somme des quantités de tous les articles
```

### Conventions monétaires

Les montants sont exprimés en **unités mineures** (centimes) : `300` = 3,00 €.

L'API Uber utilise également un format `amount_e5` (×10⁵) pour certains champs — la propriété `.amount` de `CurrencyAmount` retourne automatiquement la valeur lisible.

### Pattern factory pour les promotions

`parse_promotion(data)` retourne le sous-type approprié selon le champ `promo_type` :

| `promo_type` | Classe retournée |
|---|---|
| `FLATOFF` | `FlatOffPromotion` |
| `PERCENTOFF` | `PercentOffPromotion` |
| `FREEDELIVERY` | `FreeDeliveryPromotion` |
| autres | `BasePromotion` |
