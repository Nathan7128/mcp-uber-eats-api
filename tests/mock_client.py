"""MockUberEatsClient — client HTTP simulé pour les tests sans credentials réels.

Remplace get() / post() / delete() par un routeur interne basé sur des regex.
Retourne les fixtures définies dans tests/fixtures.py.

Usage:
    from tests.mock_client import MockUberEatsClient
    client = MockUberEatsClient()
    stores = client.stores.list()           # retourne StoreList mockée
    order = client.orders.get("any-id")    # retourne RestaurantOrder mocké
"""

import copy
import re

from api.client import UberEatsClient
from tests import fixtures

# ---------------------------------------------------------------------------
# Table de routage : (méthode HTTP) -> [(regex_chemin, fixture_dict)]
#
# Les patterns sont évalués dans l'ordre — mettre les plus spécifiques en premier.
# La regex est comparée avec re.fullmatch() sur le chemin seul (sans base URL).
# ---------------------------------------------------------------------------

_GET_ROUTES: list[tuple[str, dict]] = [
    # Stores (pluriel) — liste
    (r"/v1/delivery/stores", fixtures.STORE_LIST),
    # Store (singulier) — status
    (r"/v1/delivery/store/[^/]+/status", fixtures.STORE_STATUS_ONLINE),
    # Store (singulier) — liste des commandes
    (r"/v1/delivery/store/[^/]+/orders", fixtures.ORDER_LIST),
    # Store (singulier) — détail
    (r"/v1/delivery/store/[^/]+", fixtures.STORE_1),
    # Commande individuelle
    (r"/v1/delivery/order/[^/]+", fixtures.RESTAURANT_ORDER),
    # Promotion individuelle
    (r"/v1/delivery/promotions/[^/]+", fixtures.PROMOTION_FLATOFF),
    # Liste des promotions d'un store (pluriel "stores")
    (r"/v1/delivery/stores/[^/]+/promotions", fixtures.PROMOTION_LIST),
]

_POST_ROUTES: list[tuple[str, dict]] = [
    # Promotion — création (pluriel "stores")
    (r"/v1/delivery/stores/[^/]+/promotion", fixtures.CREATE_PROMOTION_RESPONSE),
    # Store actions (les plus spécifiques d'abord)
    (r"/v1/delivery/store/[^/]+/update-store-status", fixtures.STORE_1),
    (r"/v1/delivery/store/[^/]+/update-store-prep-time", {}),
    (r"/v1/delivery/store/[^/]+/update-fulfillment-configuration", {}),
    # Store — mise à jour générique
    (r"/v1/delivery/store/[^/]+", fixtures.STORE_1),
    # Order actions (les plus spécifiques d'abord)
    (r"/v1/delivery/order/[^/]+/adjust-price", fixtures.ADJUST_PRICE_RESPONSE),
    (r"/v1/delivery/order/[^/]+/accept", {}),
    (r"/v1/delivery/order/[^/]+/deny", {}),
    (r"/v1/delivery/order/[^/]+/cancel", {}),
    (r"/v1/delivery/order/[^/]+/ready", {}),
    (r"/v1/delivery/order/[^/]+/update-ready-time", {}),
    (r"/v1/delivery/order/[^/]+/resolve-fulfillment-issues", {}),
    (r"/v1/delivery/order/get-replacement-recommendations", {"recommendations": []}),
]

_DELETE_ROUTES: list[tuple[str, dict]] = [
    (r"/v1/delivery/promotions/[^/]+", {}),
]

_ROUTES: dict[str, list[tuple[str, dict]]] = {
    "GET": _GET_ROUTES,
    "POST": _POST_ROUTES,
    "DELETE": _DELETE_ROUTES,
}


class MockUberEatsClient(UberEatsClient):
    """Client Uber Eats simulé — aucun appel réseau réel.

    Hérite de UberEatsClient pour réutiliser les service accessors (.stores,
    .orders, .promotions…) et les lazy-loaders. Seules les méthodes HTTP
    bas-niveau (get / post / delete) sont remplacées.

    Exemple:
        client = MockUberEatsClient()
        store_list = client.stores.list()
        print(store_list.data[0].name)  # "Mock Burger Palace"
    """

    def __init__(self):
        # On passe des valeurs fictives pour ne pas lire le .env
        super().__init__(token="mock-token", base_url="http://mock-uber-eats.local")

    # ------------------------------------------------------------------
    # Méthodes HTTP overridées — pas d'appels réseau
    # ------------------------------------------------------------------

    def get(self, path: str, params: dict = None) -> dict:
        return self._dispatch("GET", path)

    def post(self, path: str, json: dict = None) -> dict:
        return self._dispatch("POST", path)

    def delete(self, path: str) -> dict:
        return self._dispatch("DELETE", path)

    # ------------------------------------------------------------------
    # Routeur interne
    # ------------------------------------------------------------------

    def _dispatch(self, method: str, path: str) -> dict:
        for pattern, fixture in _ROUTES.get(method, []):
            if re.fullmatch(pattern, path):
                # deepcopy pour éviter la mutation des fixtures entre tests
                return copy.deepcopy(fixture)
        raise ValueError(
            f"[MockUberEatsClient] Aucune route mock pour {method} {path}\n"
            f"Ajoutez une entrée dans _ROUTES dans tests/mock_client.py"
        )
