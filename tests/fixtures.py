"""Fake Uber Eats API responses mimicking sandbox/production structure."""

# ──────────────────────────────────────────────────────────────────────────────
# Stores
# ──────────────────────────────────────────────────────────────────────────────

STORE_RAW = {
    "store_id": "store-abc-123",
    "name": "Le Bistro du Coin",
    # Uber Eats returns address inside "location", not "address"
    "location": {
        "street_address_line_one": "12 rue de la Paix",
        "city": "Paris",
        "country": "FR",
        "postal_code": "75001",
    },
    "contact": {
        "name": "Jean Dupont",
        "email": "jean@bistro.fr",
        "phone_number": "+33612345678",
    },
    "timezone": "Europe/Paris",
    "onboarding_status": "ONBOARDED",
    "auto_accept": False,
    "prep_times": {"default_value": 900},
    "uber_merchant_type": {"type": "RESTAURANT"},
    # Extra API fields that should be ignored by the model
    "posId": "irrelevant",
    "merchantUUID": "irrelevant",
}

STORE_LIST_RAW = {
    "data": [STORE_RAW],
    "pagination_data": {"next_page_token": "tok-page-2", "total_count": 1},
}

STORE_LIST_EMPTY_RAW = {
    "data": [],
    "pagination_data": {},
}

STORE_STATUS_ONLINE_RAW = {
    "status": "ONLINE",
    "reason": None,
    "is_offline_until": None,
}

STORE_STATUS_OFFLINE_RAW = {
    "status": "OFFLINE",
    "reason": "CLOSED",
    "is_offline_until": "2026-03-15T18:00:00Z",
}

# ──────────────────────────────────────────────────────────────────────────────
# Orders
# ──────────────────────────────────────────────────────────────────────────────

ORDER_ITEM_RAW = {
    "id": "item-001",
    "title": "Burger Classique",
    "quantity": {"amount": 2},
    "customer_request": {"special_instructions": "Sans oignon"},
    "selected_modifier_groups": [
        {
            "title": "Cuisson",
            "selected_items": [{"title": "À point"}],
        }
    ],
}

ORDER_ITEM_SIMPLE_RAW = {
    "id": "item-002",
    "title": "Frites",
    "quantity": {"amount": 1},
}

def _order_items():
    """Return fresh item dicts each time — avoids in-place mutation by model validators."""
    return [
        {
            "id": "item-001",
            "title": "Burger Classique",
            "quantity": {"amount": 2},
            "customer_request": {"special_instructions": "Sans oignon"},
            "selected_modifier_groups": [
                {
                    "title": "Cuisson",
                    "selected_items": [{"title": "À point"}],
                }
            ],
        },
        {
            "id": "item-002",
            "title": "Frites",
            "quantity": {"amount": 1},
        },
    ]


def _order_inner(order_id="order-xyz-456", display_id="#1234"):
    """Return a fresh order dict each time — avoids in-place mutation by model validators."""
    return {
        "id": order_id,
        "display_id": display_id,
        "state": "ACCEPTED",
        "status": "ACTIVE",
        "fulfillment_type": "DELIVERY",
        "customers": [
            {
                "is_primary_customer": True,
                "name": {
                    "display_name": "Marie Martin",
                    "first_name": "Marie",
                    "last_name": "Martin",
                },
                "contact": {
                    "phone": {"number": "+33687654321"}
                },
            }
        ],
        "carts": [{"items": _order_items()}],
        "deliveries": [{"status": "COURIER_ASSIGNED"}],
        "created_time": "2026-03-15T12:00:00Z",
        "ready_for_pickup_time": "2026-03-15T12:15:00Z",
        "store_instructions": "Sonner à l'interphone",
    }


ORDER_INNER_RAW = _order_inner()

# The API wraps the order in {"order": {...}}
ORDER_RAW = {"order": _order_inner()}

ORDER_LIST_RAW = {
    "data": [
        {"order": _order_inner("order-xyz-456", "#1234")},
        {"order": _order_inner("order-xyz-789", "#1235")},
    ],
    "pagination_data": {
        "next_page_token": None,
        "total_count": 2,
    },
}

# ──────────────────────────────────────────────────────────────────────────────
# Promotions
# ──────────────────────────────────────────────────────────────────────────────

PROMOTION_PERCENTOFF_RAW = {
    "promotion_id": "promo-001",
    "store_id": "store-abc-123",
    "promo_type": "PERCENTOFF",
    "state": "ACTIVE",
    "start_time": "2026-03-01T00:00:00Z",
    "end_time": "2026-03-31T23:59:59Z",
    "currency_code": "EUR",
    "promotion_customization": {"user_group": "ALL_EATERS"},
    "percent_off_discount": {"discount_percentage": 20, "max_discount_value": 5000},
    # Other discount keys that should be ignored
    "flat_off_discount": None,
    "bogo_discount": None,
}

PROMOTION_FLATOFF_RAW = {
    "promotion_id": "promo-002",
    "store_id": "store-abc-123",
    "promo_type": "FLATOFF",
    "state": "ACTIVE",
    "start_time": "2026-03-01T00:00:00Z",
    "end_time": "2026-03-31T23:59:59Z",
    "currency_code": "EUR",
    "promotion_customization": {"user_group": "NEW_EATERS"},
    "flat_off_discount": {"discount_value": 300, "min_basket_value": 1500},
    "percent_off_discount": None,
}

PROMOTION_LIST_RAW = {
    "promotions": [PROMOTION_PERCENTOFF_RAW, PROMOTION_FLATOFF_RAW],
}
