"""Fake API responses mirroring the real Uber Eats API structure.

These fixtures are used by MockUberEatsClient to test services without real credentials.
All IDs and data are fictional.
"""

# ---------------------------------------------------------------------------
# Shared IDs (import in tests for assertions)
# ---------------------------------------------------------------------------

STORE_ID = "store-abc-1111"
STORE_ID_2 = "store-abc-2222"
ORDER_ID = "order-xyz-9999"
ORDER_ID_2 = "order-xyz-8888"
PROMO_ID_FLAT = "promo-flat-0001"
PROMO_ID_PCT = "promo-pct-0002"
PROMO_ID_NEW = "promo-new-0099"

# ---------------------------------------------------------------------------
# Stores
# ---------------------------------------------------------------------------

STORE_1: dict = {
    "id": STORE_ID,
    "name": "Mock Burger Palace",
    "contact": {
        "email": "contact@burgerpalace.fr",
        "phone_number": "+33612345678",
    },
    "location": {
        "latitude": "48.8566",
        "longitude": "2.3522",
        "street_address_line_one": "10 Rue de la Paix",
        "city": "Paris",
        "country": "FR",
        "postal_code": "75001",
    },
    "timezone": "Europe/Paris",
    "onboarding_status": "ACTIVE",
    "auto_accept": False,
    "fulfillment_type_availability": {
        "DELIVERY_BY_UBER": True,
        "PICKUP": True,
        "DELIVERY_BY_MERCHANT": False,
        "DINE_IN": False,
    },
    "prep_times": {
        "default_value": 1200,
        "delay": {
            "status": {"type": "NORMAL", "delay_duration": 0},
            "allowed": True,
        },
    },
    "uber_merchant_type": {"type": "MERCHANT_TYPE_RESTAURANT"},
    "ooi_config": {
        "is_substitute_item_enabled": True,
        "is_remove_item_enabled": True,
        "is_cancel_order_enabled": False,
    },
    "adjustment_config": {
        "is_price_adjustment_enabled": True,
        "maximum_price_adjustment": 500.0,
        "requires_tax_rate_for_adjustment": False,
        "is_tax_inclusive": True,
    },
}

STORE_2: dict = {
    "id": STORE_ID_2,
    "name": "Mock Sushi Corner",
    "contact": {
        "email": "info@sushicorner.fr",
        "phone_number": "+33698765432",
    },
    "location": {
        "latitude": "48.8600",
        "longitude": "2.3400",
        "street_address_line_one": "5 Avenue des Restaurants",
        "city": "Paris",
        "country": "FR",
        "postal_code": "75002",
    },
    "timezone": "Europe/Paris",
    "onboarding_status": "ACTIVE",
    "auto_accept": True,
    "uber_merchant_type": {"type": "MERCHANT_TYPE_RESTAURANT"},
}

STORE_LIST: dict = {
    "data": [STORE_1, STORE_2],
    "pagination_data": {"next_page_token": None, "total_count": 2},
}

STORE_STATUS_ONLINE: dict = {
    "status": "ONLINE",
    "reason": None,
    "is_offline_until": None,
}

STORE_STATUS_OFFLINE: dict = {
    "status": "OFFLINE",
    "reason": "STORE_CLOSED",
    "is_offline_until": "2026-02-28T08:00:00Z",
}

# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

RESTAURANT_ORDER: dict = {
    "order": {
        "id": ORDER_ID,
        "display_id": "#1042",
        "state": "ACCEPTED",
        "status": "ACTIVE",
        "fulfillment_type": "DELIVERY_BY_UBER",
        "ordering_platform": "UBER_EATS",
        "created_time": "2026-02-27T12:00:00Z",
        "store": {"id": STORE_ID, "name": "Mock Burger Palace"},
        "customers": [
            {
                "id": "cust-0001",
                "name": {
                    "display_name": "Jean Dupont",
                    "first_name": "Jean",
                    "last_name": "Dupont",
                },
                "is_primary_customer": True,
                "contact": {
                    "phone": {"number": "+33611223344", "country_code": "FR"}
                },
                "order_history": {"past_order_count": 3},
            }
        ],
        "carts": [
            {
                "id": "cart-0001",
                "items": [
                    {
                        "id": "item-001",
                        "title": "Classic Burger",
                        "quantity": {"amount": 2.0},
                        "selected_modifier_groups": [
                            {
                                "id": "mod-size",
                                "title": "Taille",
                                "selected_items": [
                                    {"id": "opt-large", "title": "Large", "quantity": 1}
                                ],
                            }
                        ],
                    },
                    {
                        "id": "item-002",
                        "title": "Frites",
                        "quantity": {"amount": 1.0},
                    },
                ],
            }
        ],
        "deliveries": [
            {
                "id": "delivery-0001",
                "status": "EN_ROUTE_TO_PICKUP",
                "estimated_pick_up_time": "2026-02-27T12:20:00Z",
                "estimated_dropoff_time": "2026-02-27T12:40:00Z",
            }
        ],
    }
}

RESTAURANT_ORDER_2: dict = {
    "order": {
        "id": ORDER_ID_2,
        "display_id": "#1043",
        "state": "OFFERED",
        "status": "ACTIVE",
        "fulfillment_type": "PICKUP",
        "ordering_platform": "UBER_EATS",
        "created_time": "2026-02-27T13:00:00Z",
        "store": {"id": STORE_ID, "name": "Mock Burger Palace"},
        "customers": [
            {
                "id": "cust-0002",
                "name": {
                    "display_name": "Marie Martin",
                    "first_name": "Marie",
                    "last_name": "Martin",
                },
                "is_primary_customer": True,
            }
        ],
        "carts": [
            {
                "id": "cart-0002",
                "items": [
                    {
                        "id": "item-003",
                        "title": "Veggie Burger",
                        "quantity": {"amount": 1.0},
                    }
                ],
            }
        ],
    }
}

ORDER_LIST: dict = {
    "data": [RESTAURANT_ORDER, RESTAURANT_ORDER_2],
    "pagination_data": {"next_page_token": None, "total_count": 2},
}

ADJUST_PRICE_RESPONSE: dict = {
    "tax_rate_applied": False,
}

# ---------------------------------------------------------------------------
# Promotions
# ---------------------------------------------------------------------------

PROMOTION_FLATOFF: dict = {
    "promotion_id": PROMO_ID_FLAT,
    "store_id": STORE_ID,
    "promo_type": "FLATOFF",
    "state": "active",
    "start_time": "2026-02-01T00:00:00Z",
    "end_time": "2026-02-28T23:59:59Z",
    "currency_code": "EUR",
    "flat_off_discount": {
        "min_basket_constraint": {"min_spend": {"amount": 1500}},
        "discount_value": {"amount": 300},
    },
    "allow_unlimited_apply": False,
}

PROMOTION_PERCENTOFF: dict = {
    "promotion_id": PROMO_ID_PCT,
    "store_id": STORE_ID,
    "promo_type": "PERCENTOFF",
    "state": "active",
    "start_time": "2026-02-01T00:00:00Z",
    "end_time": "2026-02-28T23:59:59Z",
    "currency_code": "EUR",
    "percent_off_discount": {
        "min_basket_constraint": {"min_spend": {"amount": 1000}},
        "percent_value": 20.0,
        "max_discount_value": {"amount": 500},
    },
}

PROMOTION_FREE_DELIVERY: dict = {
    "promotion_id": "promo-fd-0003",
    "store_id": STORE_ID,
    "promo_type": "FREEDELIVERY",
    "state": "active",
    "start_time": "2026-02-01T00:00:00Z",
    "end_time": "2026-02-28T23:59:59Z",
    "currency_code": "EUR",
}

PROMOTION_LIST: dict = {
    "promotions": [PROMOTION_FLATOFF, PROMOTION_PERCENTOFF, PROMOTION_FREE_DELIVERY],
}

CREATE_PROMOTION_RESPONSE: dict = {
    "promotion_id": PROMO_ID_NEW,
}
