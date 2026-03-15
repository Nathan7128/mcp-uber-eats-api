"""Integration tests for MCP tools — client.get() is mocked, full pipeline tested."""
import copy
from unittest.mock import patch

import mcp_server.tools as tools_module
from tests.fixtures import (
    STORE_RAW,
    STORE_LIST_RAW,
    STORE_STATUS_ONLINE_RAW,
    STORE_STATUS_OFFLINE_RAW,
    ORDER_RAW,
    ORDER_LIST_RAW,
    PROMOTION_PERCENTOFF_RAW,
    PROMOTION_LIST_RAW,
)


def mock_get(response: dict):
    """Patch client.get to return a deep copy of `response` on each call.

    Deep copy is required because Pydantic model_validators mutate the input
    dict in-place (e.g. replacing nested quantity objects with scalar values).
    Without a copy, shared fixture dicts get corrupted across tests.
    """
    return patch.object(
        tools_module.client, "get", side_effect=lambda *a, **kw: copy.deepcopy(response)
    )


# ──────────────────────────────────────────────────────────────────────────────
# list_stores
# ──────────────────────────────────────────────────────────────────────────────

class TestListStoresTool:
    def test_returns_stores_list(self):
        with mock_get(STORE_LIST_RAW):
            result = tools_module.list_stores()
        assert "stores" in result
        assert len(result["stores"]) == 1

    def test_store_has_expected_keys(self):
        with mock_get(STORE_LIST_RAW):
            result = tools_module.list_stores()
        store = result["stores"][0]
        assert store["name"] == "Le Bistro du Coin"
        assert "address" in store
        assert "contact" in store
        assert store["prep_time_seconds"] == 900

    def test_pagination_token_forwarded(self):
        with mock_get(STORE_LIST_RAW):
            result = tools_module.list_stores()
        assert result.get("next_page_token") == "tok-page-2"

    def test_calls_correct_endpoint(self):
        with mock_get(STORE_LIST_RAW) as m:
            tools_module.list_stores()
        m.assert_called_once_with("/v1/delivery/stores", params=None)

    def test_passes_pagination_params(self):
        with mock_get(STORE_LIST_RAW) as m:
            tools_module.list_stores(next_page_token="tok-page-2", limit=5)
        m.assert_called_once_with(
            "/v1/delivery/stores",
            params={"next_page_token": "tok-page-2", "limit": 5},
        )

    def test_no_raw_api_keys_in_output(self):
        with mock_get(STORE_LIST_RAW):
            result = tools_module.list_stores()
        assert "data" not in result
        assert "pagination_data" not in result


# ──────────────────────────────────────────────────────────────────────────────
# get_store
# ──────────────────────────────────────────────────────────────────────────────

class TestGetStoreTool:
    def test_returns_store_data(self):
        with mock_get(STORE_RAW):
            result = tools_module.get_store("store-abc-123")
        assert result["name"] == "Le Bistro du Coin"
        assert result["merchant_type"] == "RESTAURANT"
        assert result["address"]["city"] == "Paris"

    def test_calls_correct_endpoint(self):
        with mock_get(STORE_RAW) as m:
            tools_module.get_store("store-abc-123")
        m.assert_called_once_with("/v1/delivery/store/store-abc-123", params=None)

    def test_expand_param_joined(self):
        with mock_get(STORE_RAW) as m:
            tools_module.get_store("store-abc-123", expand=["MENU", "HOURS"])
        m.assert_called_once_with(
            "/v1/delivery/store/store-abc-123",
            params={"expand": "MENU,HOURS"},
        )

    def test_no_raw_api_noise(self):
        with mock_get(STORE_RAW):
            result = tools_module.get_store("store-abc-123")
        assert "location" not in result
        assert "prep_times" not in result
        assert "uber_merchant_type" not in result
        assert "posId" not in result


# ──────────────────────────────────────────────────────────────────────────────
# get_store_status
# ──────────────────────────────────────────────────────────────────────────────

class TestGetStoreStatusTool:
    def test_online_store(self):
        with mock_get(STORE_STATUS_ONLINE_RAW):
            result = tools_module.get_store_status("store-abc-123")
        assert result["status"] == "ONLINE"
        assert result["is_online"] is True
        assert "offline_reason" not in result

    def test_offline_store(self):
        with mock_get(STORE_STATUS_OFFLINE_RAW):
            result = tools_module.get_store_status("store-abc-123")
        assert result["status"] == "OFFLINE"
        assert result["is_online"] is False
        assert result["offline_reason"] == "CLOSED"
        assert result["offline_until"] == "2026-03-15T18:00:00Z"

    def test_calls_correct_endpoint(self):
        with mock_get(STORE_STATUS_ONLINE_RAW) as m:
            tools_module.get_store_status("store-abc-123")
        m.assert_called_once_with("/v1/delivery/store/store-abc-123/status")

    def test_no_raw_api_keys(self):
        with mock_get(STORE_STATUS_OFFLINE_RAW):
            result = tools_module.get_store_status("store-abc-123")
        assert "reason" not in result
        assert "is_offline_until" not in result


# ──────────────────────────────────────────────────────────────────────────────
# get_order
# ──────────────────────────────────────────────────────────────────────────────

class TestGetOrderTool:
    def test_unwraps_order_wrapper(self):
        """The API returns {"order": {...}} — the tool must unwrap it."""
        with mock_get(ORDER_RAW):
            result = tools_module.get_order("order-xyz-456")
        assert result["id"] == "order-xyz-456"
        assert "order" not in result  # wrapper key must not leak through

    def test_customer_info_present(self):
        with mock_get(ORDER_RAW):
            result = tools_module.get_order("order-xyz-456")
        assert result["customer_name"] == "Marie Martin"
        assert result["customer_phone"] == "+33687654321"

    def test_items_flattened(self):
        with mock_get(ORDER_RAW):
            result = tools_module.get_order("order-xyz-456")
        assert "items" in result
        assert len(result["items"]) == 2
        assert result["item_count"] == 3  # 2 burgers + 1 frites

    def test_delivery_status_present(self):
        with mock_get(ORDER_RAW):
            result = tools_module.get_order("order-xyz-456")
        assert result["delivery_status"] == "COURIER_ASSIGNED"

    def test_calls_correct_endpoint(self):
        with mock_get(ORDER_RAW) as m:
            tools_module.get_order("order-xyz-456")
        m.assert_called_once_with("/v1/delivery/order/order-xyz-456", params=None)

    def test_no_raw_api_keys(self):
        with mock_get(ORDER_RAW):
            result = tools_module.get_order("order-xyz-456")
        assert "customers" not in result
        assert "carts" not in result
        assert "deliveries" not in result


# ──────────────────────────────────────────────────────────────────────────────
# list_store_orders
# ──────────────────────────────────────────────────────────────────────────────

class TestListStoreOrdersTool:
    def test_returns_orders_list(self):
        with mock_get(ORDER_LIST_RAW):
            result = tools_module.list_store_orders("store-abc-123")
        assert "orders" in result
        assert len(result["orders"]) == 2

    def test_total_count_present(self):
        with mock_get(ORDER_LIST_RAW):
            result = tools_module.list_store_orders("store-abc-123")
        assert result["total_count"] == 2

    def test_calls_correct_endpoint(self):
        with mock_get(ORDER_LIST_RAW) as m:
            tools_module.list_store_orders("store-abc-123")
        m.assert_called_once_with(
            "/v1/delivery/store/store-abc-123/orders", params=None
        )

    def test_passes_filters(self):
        with mock_get(ORDER_LIST_RAW) as m:
            tools_module.list_store_orders(
                "store-abc-123",
                state="ACCEPTED",
                status="ACTIVE",
                page_size=10,
            )
        m.assert_called_once_with(
            "/v1/delivery/store/store-abc-123/orders",
            params={"state": "ACCEPTED", "status": "ACTIVE", "page_size": 10},
        )

    def test_no_raw_data_key(self):
        with mock_get(ORDER_LIST_RAW):
            result = tools_module.list_store_orders("store-abc-123")
        assert "data" not in result


# ──────────────────────────────────────────────────────────────────────────────
# get_promotion
# ──────────────────────────────────────────────────────────────────────────────

class TestGetPromotionTool:
    def test_returns_promotion_data(self):
        with mock_get(PROMOTION_PERCENTOFF_RAW):
            result = tools_module.get_promotion("promo-001")
        assert result["promotion_id"] == "promo-001"
        assert result["type"] == "PERCENTOFF"
        assert result["target_customers"] == "ALL_EATERS"
        assert result["discount_details"]["discount_percentage"] == 20

    def test_calls_correct_endpoint(self):
        with mock_get(PROMOTION_PERCENTOFF_RAW) as m:
            tools_module.get_promotion("promo-001")
        m.assert_called_once_with("/v1/delivery/promotions/promo-001")

    def test_no_promo_type_alias_leak(self):
        """'promo_type' must be exposed as 'type', not both."""
        with mock_get(PROMOTION_PERCENTOFF_RAW):
            result = tools_module.get_promotion("promo-001")
        assert "type" in result
        assert "promo_type" not in result

    def test_other_discount_keys_absent(self):
        with mock_get(PROMOTION_PERCENTOFF_RAW):
            result = tools_module.get_promotion("promo-001")
        assert "flat_off_discount" not in result
        assert "bogo_discount" not in result


# ──────────────────────────────────────────────────────────────────────────────
# list_store_promotions
# ──────────────────────────────────────────────────────────────────────────────

class TestListStorePromotionsTool:
    def test_returns_promotions_list(self):
        with mock_get(PROMOTION_LIST_RAW):
            result = tools_module.list_store_promotions("store-abc-123")
        assert "promotions" in result
        assert len(result["promotions"]) == 2

    def test_promotions_are_parsed(self):
        with mock_get(PROMOTION_LIST_RAW):
            result = tools_module.list_store_promotions("store-abc-123")
        types = {p["type"] for p in result["promotions"]}
        assert types == {"PERCENTOFF", "FLATOFF"}

    def test_calls_correct_endpoint(self):
        with mock_get(PROMOTION_LIST_RAW) as m:
            tools_module.list_store_promotions("store-abc-123")
        m.assert_called_once_with("/v1/delivery/stores/store-abc-123/promotions")
