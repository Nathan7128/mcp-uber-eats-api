"""Fake Uber Eats API responses mimicking sandbox/production structure."""

# ──────────────────────────────────────────────────────────────────────────────
# Stores
# ──────────────────────────────────────────────────────────────────────────────

STORE_RAW = {
    "store_id": "store-abc-123",
    "name": "Le Bistro du Coin",
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
    "posId": "irrelevant",
    "merchantUUID": "irrelevant",
}

STORE_PIZZERIA_RAW = {
    "store_id": "store-def-456",
    "name": "La Pizzeria Napoli",
    "location": {
        "street_address_line_one": "8 place Bellecour",
        "city": "Lyon",
        "country": "FR",
        "postal_code": "69001",
    },
    "contact": {
        "name": "Marco Rossi",
        "email": "marco@napoli-lyon.fr",
        "phone_number": "+33478123456",
    },
    "timezone": "Europe/Paris",
    "onboarding_status": "ONBOARDED",
    "auto_accept": True,
    "prep_times": {"default_value": 1200},
    "uber_merchant_type": {"type": "RESTAURANT"},
}

STORE_SUSHI_RAW = {
    "store_id": "store-ghi-789",
    "name": "Sushi Zen",
    "location": {
        "street_address_line_one": "42 avenue des Champs-Élysées",
        "city": "Paris",
        "country": "FR",
        "postal_code": "75008",
    },
    "contact": {
        "name": "Yuki Tanaka",
        "email": "contact@sushizen.fr",
        "phone_number": "+33145678901",
    },
    "timezone": "Europe/Paris",
    "onboarding_status": "ONBOARDED",
    "auto_accept": True,
    "prep_times": {"default_value": 600},
    "uber_merchant_type": {"type": "RESTAURANT"},
}

STORE_BURGER_RAW = {
    "store_id": "store-jkl-012",
    "name": "Le Burger Palace",
    "location": {
        "street_address_line_one": "3 cours de l'Intendance",
        "city": "Bordeaux",
        "country": "FR",
        "postal_code": "33000",
    },
    "contact": {
        "name": "Sophie Leblanc",
        "email": "sophie@burgerpalace.fr",
        "phone_number": "+33556789012",
    },
    "timezone": "Europe/Paris",
    "onboarding_status": "ONBOARDED",
    "auto_accept": False,
    "prep_times": {"default_value": 780},
    "uber_merchant_type": {"type": "RESTAURANT"},
}

STORE_CREPE_RAW = {
    "store_id": "store-mno-345",
    "name": "La Crêperie Bretonne",
    "location": {
        "street_address_line_one": "5 rue Saint-Michel",
        "city": "Rennes",
        "country": "FR",
        "postal_code": "35000",
    },
    "contact": {
        "name": "Gwenaëlle Morin",
        "email": "gwen@creperie-bretonne.fr",
        "phone_number": "+33299345678",
    },
    "timezone": "Europe/Paris",
    "onboarding_status": "ONBOARDED",
    "auto_accept": True,
    "prep_times": {"default_value": 720},
    "uber_merchant_type": {"type": "RESTAURANT"},
}

STORE_LIST_RAW = {
    "data": [
        STORE_RAW,
        STORE_PIZZERIA_RAW,
        STORE_SUSHI_RAW,
        STORE_BURGER_RAW,
        STORE_CREPE_RAW,
    ],
    "pagination_data": {"next_page_token": None, "total_count": 5},
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

# Per-store statuses
STORE_STATUSES = {
    "store-abc-123": {"status": "ONLINE", "reason": None, "is_offline_until": None},
    "store-def-456": {"status": "ONLINE", "reason": None, "is_offline_until": None},
    "store-ghi-789": {"status": "ONLINE", "reason": None, "is_offline_until": None},
    "store-jkl-012": {"status": "OFFLINE", "reason": "PAUSED_BY_MERCHANT", "is_offline_until": "2026-03-22T20:00:00Z"},
    "store-mno-345": {"status": "ONLINE", "reason": None, "is_offline_until": None},
}

# Per-store lookup
STORES_BY_ID = {
    "store-abc-123": STORE_RAW,
    "store-def-456": STORE_PIZZERIA_RAW,
    "store-ghi-789": STORE_SUSHI_RAW,
    "store-jkl-012": STORE_BURGER_RAW,
    "store-mno-345": STORE_CREPE_RAW,
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
    """Bistro du Coin items — fresh copy each call."""
    return [
        {
            "id": "item-001",
            "title": "Burger Classique",
            "quantity": {"amount": 2},
            "customer_request": {"special_instructions": "Sans oignon"},
            "selected_modifier_groups": [
                {"title": "Cuisson", "selected_items": [{"title": "À point"}]}
            ],
        },
        {"id": "item-002", "title": "Frites", "quantity": {"amount": 1}},
    ]


def _pizza_items():
    return [
        {"id": "item-p01", "title": "Pizza Margherita", "quantity": {"amount": 1}},
        {
            "id": "item-p02",
            "title": "Pizza 4 Fromages",
            "quantity": {"amount": 1},
            "customer_request": {"special_instructions": "Sans champignons"},
        },
        {"id": "item-p03", "title": "Tiramisu", "quantity": {"amount": 2}},
    ]


def _sushi_items():
    return [
        {"id": "item-s01", "title": "Plateau Sushi 24 pièces", "quantity": {"amount": 1}},
        {"id": "item-s02", "title": "Ramen Tonkotsu", "quantity": {"amount": 2}},
        {"id": "item-s03", "title": "Edamame", "quantity": {"amount": 1}},
    ]


def _burger_items():
    return [
        {
            "id": "item-b01",
            "title": "Double Smash Burger",
            "quantity": {"amount": 2},
            "selected_modifier_groups": [
                {"title": "Sauce", "selected_items": [{"title": "BBQ"}]}
            ],
        },
        {"id": "item-b02", "title": "Onion Rings", "quantity": {"amount": 1}},
        {"id": "item-b03", "title": "Milkshake Vanille", "quantity": {"amount": 2}},
    ]


def _crepe_items():
    return [
        {
            "id": "item-c01",
            "title": "Galette Complète",
            "quantity": {"amount": 2},
            "customer_request": {"special_instructions": "Œuf bien cuit"},
        },
        {"id": "item-c02", "title": "Crêpe Caramel Beurre Salé", "quantity": {"amount": 3}},
        {"id": "item-c03", "title": "Cidre Breton", "quantity": {"amount": 2}},
    ]


def _order_inner(order_id="order-xyz-456", display_id="#1234", customer_name="Marie Martin",
                 customer_phone="+33687654321", items_fn=None, state="ACCEPTED",
                 fulfillment_type="DELIVERY", delivery_status="COURIER_ASSIGNED",
                 created_time="2026-03-15T12:00:00Z", store_instructions=None):
    """Return a fresh order dict each time — avoids in-place mutation by model validators."""
    if items_fn is None:
        items_fn = _order_items
    first_name, *rest = customer_name.split(" ", 1)
    last_name = rest[0] if rest else ""
    order = {
        "id": order_id,
        "display_id": display_id,
        "state": state,
        "status": "ACTIVE" if state in {"ACCEPTED", "OFFERED", "CREATED"} else "COMPLETED",
        "fulfillment_type": fulfillment_type,
        "customers": [
            {
                "is_primary_customer": True,
                "name": {
                    "display_name": customer_name,
                    "first_name": first_name,
                    "last_name": last_name,
                },
                "contact": {"phone": {"number": customer_phone}},
            }
        ],
        "carts": [{"items": items_fn()}],
        "deliveries": [{"status": delivery_status}],
        "created_time": created_time,
        "ready_for_pickup_time": created_time.replace("T12:00", "T12:15").replace("T10:00", "T10:15").replace("T14:00", "T14:15").replace("T19:00", "T19:15").replace("T20:00", "T20:15"),
    }
    if store_instructions:
        order["store_instructions"] = store_instructions
    return order


ORDER_INNER_RAW = _order_inner()

# The API wraps the order in {"order": {...}}
ORDER_RAW = {"order": _order_inner()}

# ── Bistro du Coin (store-abc-123) ───────────────────────────────────────────

ORDER_LIST_RAW = {
    "data": [
        {"order": _order_inner("order-xyz-456", "#1234", "Marie Martin", "+33687654321",
                               _order_items, "ACCEPTED", "DELIVERY", "COURIER_ASSIGNED",
                               "2026-03-22T12:00:00Z", "Sonner à l'interphone")},
        {"order": _order_inner("order-xyz-789", "#1235", "Paul Bernard", "+33698765432",
                               _order_items, "ACCEPTED", "DELIVERY", "COURIER_PICKED_UP",
                               "2026-03-22T12:30:00Z")},
        {"order": _order_inner("order-xyz-999", "#1236", "Camille Petit", "+33611223344",
                               _order_items, "SUCCEEDED", "PICKUP", "DELIVERED",
                               "2026-03-22T11:00:00Z")},
    ],
    "pagination_data": {"next_page_token": None, "total_count": 3},
}

# ── Pizzeria Napoli (store-def-456) ──────────────────────────────────────────

ORDER_LIST_PIZZERIA_RAW = {
    "data": [
        {"order": _order_inner("order-piz-001", "#2001", "Lucas Fontaine", "+33622334455",
                               _pizza_items, "ACCEPTED", "DELIVERY", "COURIER_ASSIGNED",
                               "2026-03-22T19:00:00Z", "Code portail : 4512")},
        {"order": _order_inner("order-piz-002", "#2002", "Inès Moreau", "+33633445566",
                               _pizza_items, "CREATED", "DELIVERY", "PENDING",
                               "2026-03-22T19:20:00Z")},
        {"order": _order_inner("order-piz-003", "#2003", "Tom Girard", "+33644556677",
                               _pizza_items, "ACCEPTED", "PICKUP", "NOT_APPLICABLE",
                               "2026-03-22T18:45:00Z")},
    ],
    "pagination_data": {"next_page_token": None, "total_count": 3},
}

# ── Sushi Zen (store-ghi-789) ────────────────────────────────────────────────

ORDER_LIST_SUSHI_RAW = {
    "data": [
        {"order": _order_inner("order-sus-001", "#3001", "Amélie Dubois", "+33655667788",
                               _sushi_items, "ACCEPTED", "DELIVERY", "COURIER_ASSIGNED",
                               "2026-03-22T20:00:00Z")},
        {"order": _order_inner("order-sus-002", "#3002", "Romain Leroy", "+33666778899",
                               _sushi_items, "ACCEPTED", "DELIVERY", "COURIER_ASSIGNED",
                               "2026-03-22T20:10:00Z", "Pas d'allergies")},
    ],
    "pagination_data": {"next_page_token": None, "total_count": 2},
}

# ── Burger Palace (store-jkl-012) ────────────────────────────────────────────

ORDER_LIST_BURGER_RAW = {
    "data": [
        {"order": _order_inner("order-bur-001", "#4001", "Jade Simon", "+33677889900",
                               _burger_items, "SUCCEEDED", "DELIVERY", "DELIVERED",
                               "2026-03-22T14:00:00Z")},
        {"order": _order_inner("order-bur-002", "#4002", "Hugo Laurent", "+33688990011",
                               _burger_items, "SUCCEEDED", "DELIVERY", "DELIVERED",
                               "2026-03-22T13:00:00Z")},
        {"order": _order_inner("order-bur-003", "#4003", "Chloé Mercier", "+33699001122",
                               _burger_items, "ACCEPTED", "PICKUP", "NOT_APPLICABLE",
                               "2026-03-22T14:30:00Z")},
    ],
    "pagination_data": {"next_page_token": None, "total_count": 3},
}

# ── Crêperie Bretonne (store-mno-345) ────────────────────────────────────────

ORDER_LIST_CREPE_RAW = {
    "data": [
        {"order": _order_inner("order-cre-001", "#5001", "Mathilde Rousseau", "+33611002233",
                               _crepe_items, "ACCEPTED", "DELIVERY", "COURIER_ASSIGNED",
                               "2026-03-22T12:00:00Z")},
        {"order": _order_inner("order-cre-002", "#5002", "Antoine Blanchard", "+33622113344",
                               _crepe_items, "CREATED", "DELIVERY", "PENDING",
                               "2026-03-22T12:20:00Z", "Interphone 3B")},
    ],
    "pagination_data": {"next_page_token": None, "total_count": 2},
}

# Per-store order lists
ORDER_LISTS_BY_STORE = {
    "store-abc-123": ORDER_LIST_RAW,
    "store-def-456": ORDER_LIST_PIZZERIA_RAW,
    "store-ghi-789": ORDER_LIST_SUSHI_RAW,
    "store-jkl-012": ORDER_LIST_BURGER_RAW,
    "store-mno-345": ORDER_LIST_CREPE_RAW,
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

# Per-store promotions
PROMOTIONS_BY_STORE = {
    "store-abc-123": PROMOTION_LIST_RAW,
    "store-def-456": {
        "promotions": [
            {
                "promotion_id": "promo-003",
                "store_id": "store-def-456",
                "promo_type": "PERCENTOFF",
                "state": "ACTIVE",
                "start_time": "2026-03-15T00:00:00Z",
                "end_time": "2026-03-31T23:59:59Z",
                "currency_code": "EUR",
                "promotion_customization": {"user_group": "ALL_EATERS"},
                "percent_off_discount": {"discount_percentage": 15, "max_discount_value": 3000},
                "flat_off_discount": None,
                "bogo_discount": None,
            }
        ]
    },
    "store-ghi-789": {
        "promotions": [
            {
                "promotion_id": "promo-004",
                "store_id": "store-ghi-789",
                "promo_type": "FLATOFF",
                "state": "ACTIVE",
                "start_time": "2026-03-20T00:00:00Z",
                "end_time": "2026-04-20T23:59:59Z",
                "currency_code": "EUR",
                "promotion_customization": {"user_group": "NEW_EATERS"},
                "flat_off_discount": {"discount_value": 500, "min_basket_value": 2500},
                "percent_off_discount": None,
            }
        ]
    },
    "store-jkl-012": {
        "promotions": [
            {
                "promotion_id": "promo-005",
                "store_id": "store-jkl-012",
                "promo_type": "PERCENTOFF",
                "state": "ACTIVE",
                "start_time": "2026-03-01T00:00:00Z",
                "end_time": "2026-03-31T23:59:59Z",
                "currency_code": "EUR",
                "promotion_customization": {"user_group": "ALL_EATERS"},
                "percent_off_discount": {"discount_percentage": 10, "max_discount_value": 2000},
                "flat_off_discount": None,
                "bogo_discount": None,
            }
        ]
    },
    "store-mno-345": {"promotions": []},
}
