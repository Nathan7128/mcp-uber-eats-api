"""Client synthétique utilisant les fakes données du fichier `fixtures.py`."""
import copy
import re

from mcp_server.mocks.fixtures import (
    STORE_LIST_RAW,
    STORE_STATUS_ONLINE_RAW,
    STORES_BY_ID,
    STORE_STATUSES,
    ORDER_RAW,
    ORDER_LISTS_BY_STORE,
    ORDERS_BY_ID,
    PROMOTIONS_BY_STORE,
    PROMOTIONS_BY_ID,
)

# Synthétiques routes utilisées par le Mock client afin de remplacer les vrais route de l'API
# Implémentation des méthodes Get seulement pour ce Mock client.
_ROUTES = [
    # GET /v1/delivery/stores/{store_id}/promotions
    (re.compile(r"^/v1/delivery/stores/(?P<store_id>[^/]+)/promotions$"),
     lambda m: PROMOTIONS_BY_STORE.get(m.group("store_id"), {"promotions": []})),

    # GET /v1/delivery/stores
    (re.compile(r"^/v1/delivery/stores$"),
     lambda m: STORE_LIST_RAW),

    # GET /v1/delivery/store/{store_id}/status
    (re.compile(r"^/v1/delivery/store/(?P<store_id>[^/]+)/status$"),
     lambda m: STORE_STATUSES.get(m.group("store_id"), STORE_STATUS_ONLINE_RAW)),

    # GET /v1/delivery/store/{store_id}/orders
    (re.compile(r"^/v1/delivery/store/(?P<store_id>[^/]+)/orders$"),
     lambda m: ORDER_LISTS_BY_STORE.get(m.group("store_id"), {"data": [], "pagination_data": {}})),

    # GET /v1/delivery/store/{store_id}
    (re.compile(r"^/v1/delivery/store/(?P<store_id>[^/]+)$"),
     lambda m: STORES_BY_ID.get(m.group("store_id"), next(iter(STORES_BY_ID.values())))),

    # GET /v1/delivery/order/{order_id}
    (re.compile(r"^/v1/delivery/order/(?P<order_id>[^/]+)$"),
     lambda m: ORDERS_BY_ID.get(m.group("order_id"), ORDER_RAW)),

    # GET /v1/delivery/promotions/{promotion_id}
    (re.compile(r"^/v1/delivery/promotions/(?P<promotion_id>[^/]+)$"),
     lambda m: PROMOTIONS_BY_ID.get(m.group("promotion_id"), next(iter(PROMOTIONS_BY_ID.values())))),
]


class MockUberEatsClient:
    """Client synthétique permettant de simuler le comportement d'un vrai client qui serait connecté à l'API Uber Eats.  
    
    Utilise les données synthétiques du fichier `fixtures.py` et les fakes Routes définies au préalable.
    Ce client est limité aux commandes Get.
    """
    
    def get(self, path: str, params: dict | None = None) -> dict:
        # Parcours toutes les fakes Routes disponibles pour trouver celle qui correspond à celle passée en paramètre lors
        # de l'appel du tools MCP.
        for pattern, factory in _ROUTES:
            match = pattern.match(path)
            if match:
                return copy.deepcopy(factory(match))
        raise ValueError(f"MockUberEatsClient: unhandled path: {path}")
