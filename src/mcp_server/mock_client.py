"""Mock client returning fixture data — used when MOCK_API=true.

Activated automatically by tools.py when the MOCK_API environment variable
is set to '1', 'true', or 'yes'. Routes are matched via regex against the
path argument, mirroring the real Uber Eats API URL structure.
"""
import copy
import re
import sys
from typing import Any

from tests.fixtures import (
    STORE_LIST_RAW,
    STORE_STATUS_ONLINE_RAW,
    STORES_BY_ID,
    STORE_STATUSES,
    ORDER_RAW,
    ORDER_LIST_RAW,
    ORDER_LISTS_BY_STORE,
    PROMOTIONS_BY_STORE,
    PROMOTION_LIST_RAW,
    PROMOTION_PERCENTOFF_RAW,
)

print("[MOCK] MockUberEatsClient module loaded", file=sys.stderr, flush=True)

# Patterns ordered from most specific to least specific
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
     lambda m: ORDER_LISTS_BY_STORE.get(m.group("store_id"), ORDER_LIST_RAW)),

    # GET /v1/delivery/store/{store_id}
    (re.compile(r"^/v1/delivery/store/(?P<store_id>[^/]+)$"),
     lambda m: STORES_BY_ID.get(m.group("store_id"), next(iter(STORES_BY_ID.values())))),

    # GET /v1/delivery/order/{order_id}
    (re.compile(r"^/v1/delivery/order/(?P<order_id>[^/]+)$"),
     lambda m: ORDER_RAW),

    # GET /v1/delivery/promotions/{promotion_id}
    (re.compile(r"^/v1/delivery/promotions/(?P<promotion_id>[^/]+)$"),
     lambda m: PROMOTION_PERCENTOFF_RAW),
]


class MockUberEatsClient:
    def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        for pattern, factory in _ROUTES:
            match = pattern.match(path)
            if match:
                data = factory(match)
                print(f"[MOCK] GET {path} → {list(data.keys())}", file=sys.stderr, flush=True)
                return copy.deepcopy(data)
        raise ValueError(f"MockUberEatsClient: chemin non géré : {path}")
