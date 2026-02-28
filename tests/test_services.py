"""Tests des services Uber Eats avec MockUberEatsClient.

Lance avec :
    python -m pytest tests/                  # si pytest est installé
    python -m unittest discover tests/       # avec la stdlib uniquement
    uv run python -m pytest tests/ -v        # avec uv
"""

import unittest

from api.models.orders import (
    AdjustPriceResponse,
    OrderList,
    RestaurantOrder,
)
from api.models.promotions import (
    BasePromotion,
    CreatePromotionResponse,
    FlatOffPromotion,
    FreeDeliveryPromotion,
    PercentOffPromotion,
    PromotionList,
)
from api.models.stores import Store, StoreList, StoreStatusResponse
from tests import fixtures
from tests.mock_client import MockUberEatsClient


class TestStoresService(unittest.TestCase):
    """Tests du StoresService avec données mockées."""

    def setUp(self):
        self.client = MockUberEatsClient()

    # --- list() ---

    def test_list_returns_store_list(self):
        result = self.client.stores.list()
        self.assertIsInstance(result, StoreList)

    def test_list_contains_two_stores(self):
        result = self.client.stores.list()
        self.assertEqual(len(result.data), 2)

    def test_list_first_store_fields(self):
        result = self.client.stores.list()
        store = result.data[0]
        self.assertEqual(store.id, fixtures.STORE_ID)
        self.assertEqual(store.name, "Mock Burger Palace")
        self.assertEqual(store.location.city, "Paris")
        self.assertEqual(store.location.country, "FR")

    def test_list_pagination_data(self):
        result = self.client.stores.list()
        self.assertIsNotNone(result.pagination_data)

    # --- get() ---

    def test_get_returns_store(self):
        result = self.client.stores.get(fixtures.STORE_ID)
        self.assertIsInstance(result, Store)

    def test_get_store_id_and_name(self):
        result = self.client.stores.get(fixtures.STORE_ID)
        self.assertEqual(result.id, fixtures.STORE_ID)
        self.assertEqual(result.name, "Mock Burger Palace")

    def test_get_store_fulfillment_types(self):
        result = self.client.stores.get(fixtures.STORE_ID)
        self.assertTrue(result.fulfillment_type_availability.DELIVERY_BY_UBER)
        self.assertTrue(result.fulfillment_type_availability.PICKUP)
        self.assertFalse(result.fulfillment_type_availability.DELIVERY_BY_MERCHANT)

    def test_get_store_prep_time(self):
        result = self.client.stores.get(fixtures.STORE_ID)
        self.assertEqual(result.prep_times.default_value, 1200)

    def test_get_store_ooi_config(self):
        result = self.client.stores.get(fixtures.STORE_ID)
        self.assertTrue(result.ooi_config.is_substitute_item_enabled)

    # --- get_status() ---

    def test_get_status_returns_store_status_response(self):
        result = self.client.stores.get_status(fixtures.STORE_ID)
        self.assertIsInstance(result, StoreStatusResponse)

    def test_get_status_is_online(self):
        result = self.client.stores.get_status(fixtures.STORE_ID)
        self.assertTrue(result.is_online)

    def test_get_status_enum_value(self):
        from api.models.stores import StoreStatusEnum
        result = self.client.stores.get_status(fixtures.STORE_ID)
        self.assertEqual(result.status, StoreStatusEnum.ONLINE)

    # --- update() ---

    def test_update_returns_store(self):
        result = self.client.stores.update(
            fixtures.STORE_ID,
            contact={"phone": "+33600000000"},
        )
        self.assertIsInstance(result, Store)

    # --- update_status() ---

    def test_update_status_online(self):
        result = self.client.stores.update_status(fixtures.STORE_ID, "ONLINE")
        self.assertIsInstance(result, Store)

    def test_update_status_offline_with_reason(self):
        result = self.client.stores.update_status(
            fixtures.STORE_ID, "OFFLINE", reason="STORE_CLOSED"
        )
        self.assertIsInstance(result, Store)

    # --- update_prep_time() ---

    def test_update_prep_time_returns_dict(self):
        result = self.client.stores.update_prep_time(fixtures.STORE_ID, 20, 30)
        self.assertIsInstance(result, dict)

    # --- update_fulfillment_config() ---

    def test_update_fulfillment_config_returns_dict(self):
        result = self.client.stores.update_fulfillment_config(
            fixtures.STORE_ID, {"custom_min_etd_minutes": 45}
        )
        self.assertIsInstance(result, dict)

    # --- repr ---

    def test_store_repr(self):
        store = self.client.stores.get(fixtures.STORE_ID)
        self.assertIn(fixtures.STORE_ID, repr(store))


class TestOrdersService(unittest.TestCase):
    """Tests du OrdersService avec données mockées."""

    def setUp(self):
        self.client = MockUberEatsClient()

    # --- get() ---

    def test_get_returns_restaurant_order(self):
        result = self.client.orders.get(fixtures.ORDER_ID)
        self.assertIsInstance(result, RestaurantOrder)

    def test_get_order_inner_fields(self):
        result = self.client.orders.get(fixtures.ORDER_ID)
        order = result.order
        self.assertEqual(order.id, fixtures.ORDER_ID)
        self.assertEqual(order.display_id, "#1042")

    def test_get_order_state_and_status(self):
        from api.models.orders import OrderState, OrderStatus
        result = self.client.orders.get(fixtures.ORDER_ID)
        self.assertEqual(result.order.state, OrderState.ACCEPTED)
        self.assertEqual(result.order.status, OrderStatus.ACTIVE)

    # --- primary_customer property ---

    def test_order_primary_customer(self):
        result = self.client.orders.get(fixtures.ORDER_ID)
        customer = result.order.primary_customer
        self.assertIsNotNone(customer)
        self.assertTrue(customer.is_primary_customer)
        self.assertEqual(str(customer.name), "Jean Dupont")

    # --- item_count property ---

    def test_order_item_count(self):
        result = self.client.orders.get(fixtures.ORDER_ID)
        # 2× Classic Burger + 1× Frites
        self.assertEqual(result.order.item_count, 3)

    # --- deliveries ---

    def test_order_delivery_status(self):
        from api.models.orders import DeliveryStatus
        result = self.client.orders.get(fixtures.ORDER_ID)
        delivery = result.order.deliveries[0]
        self.assertEqual(delivery.status, DeliveryStatus.EN_ROUTE_TO_PICKUP)

    # --- list() ---

    def test_list_returns_order_list(self):
        result = self.client.orders.list(fixtures.STORE_ID)
        self.assertIsInstance(result, OrderList)

    def test_list_orders_helper(self):
        result = self.client.orders.list(fixtures.STORE_ID)
        orders = result.orders
        self.assertEqual(len(orders), 2)

    def test_list_orders_ids(self):
        result = self.client.orders.list(fixtures.STORE_ID)
        ids = [o.id for o in result.orders]
        self.assertIn(fixtures.ORDER_ID, ids)
        self.assertIn(fixtures.ORDER_ID_2, ids)

    # --- accept() ---

    def test_accept_returns_dict(self):
        result = self.client.orders.accept(
            fixtures.ORDER_ID,
            ready_for_pickup_time="2026-02-27T12:20:00Z",
        )
        self.assertIsInstance(result, dict)

    # --- deny() ---

    def test_deny_returns_dict(self):
        result = self.client.orders.deny(fixtures.ORDER_ID, reason="ITEM_UNAVAILABLE")
        self.assertIsInstance(result, dict)

    # --- cancel() ---

    def test_cancel_returns_dict(self):
        result = self.client.orders.cancel(fixtures.ORDER_ID, reason="KITCHEN_CLOSED")
        self.assertIsInstance(result, dict)

    # --- mark_ready() ---

    def test_mark_ready_returns_dict(self):
        result = self.client.orders.mark_ready(fixtures.ORDER_ID)
        self.assertIsInstance(result, dict)

    # --- adjust_price() ---

    def test_adjust_price_returns_typed_response(self):
        result = self.client.orders.adjust_price(
            fixtures.ORDER_ID,
            items=[{"item_id": "item-001", "price": {"amount": 599, "currency_code": "EUR"}}],
        )
        self.assertIsInstance(result, AdjustPriceResponse)
        self.assertFalse(result.tax_rate_applied)

    # --- update_ready_time() ---

    def test_update_ready_time_returns_dict(self):
        result = self.client.orders.update_ready_time(
            fixtures.ORDER_ID, "2026-02-27T12:30:00Z"
        )
        self.assertIsInstance(result, dict)

    # --- resolve_fulfillment_issues() ---

    def test_resolve_fulfillment_issues_returns_dict(self):
        result = self.client.orders.resolve_fulfillment_issues(
            fixtures.ORDER_ID,
            resolution={"items_unavailable": [{"item_id": "item-002", "quantity": 1}]},
        )
        self.assertIsInstance(result, dict)

    # --- get_replacement_recommendations() ---

    def test_get_replacement_recommendations_returns_dict(self):
        result = self.client.orders.get_replacement_recommendations(
            items=[{"item_id": "item-002", "quantity": 1}],
            store_id=fixtures.STORE_ID,
        )
        self.assertIsInstance(result, dict)
        self.assertIn("recommendations", result)

    # --- repr ---

    def test_order_repr(self):
        result = self.client.orders.get(fixtures.ORDER_ID)
        self.assertIn(fixtures.ORDER_ID, repr(result.order))


class TestPromotionsService(unittest.TestCase):
    """Tests du PromotionsService avec données mockées."""

    def setUp(self):
        self.client = MockUberEatsClient()

    # --- get() ---

    def test_get_returns_base_promotion(self):
        result = self.client.promotions.get(fixtures.PROMO_ID_FLAT)
        self.assertIsInstance(result, BasePromotion)

    def test_get_flat_off_promotion_type(self):
        result = self.client.promotions.get(fixtures.PROMO_ID_FLAT)
        self.assertIsInstance(result, FlatOffPromotion)

    def test_get_flat_off_fields(self):
        result = self.client.promotions.get(fixtures.PROMO_ID_FLAT)
        self.assertEqual(result.promotion_id, fixtures.PROMO_ID_FLAT)
        self.assertEqual(result.currency_code, "EUR")
        self.assertIsNotNone(result.flat_off_discount)

    def test_get_promotion_state(self):
        from api.models.promotions import PromotionState
        result = self.client.promotions.get(fixtures.PROMO_ID_FLAT)
        self.assertEqual(result.state, PromotionState.ACTIVE)

    # --- list() ---

    def test_list_returns_promotion_list(self):
        result = self.client.promotions.list(fixtures.STORE_ID)
        self.assertIsInstance(result, PromotionList)

    def test_list_contains_three_promotions(self):
        result = self.client.promotions.list(fixtures.STORE_ID)
        self.assertEqual(len(result.promotions), 3)

    def test_list_promotions_are_typed(self):
        result = self.client.promotions.list(fixtures.STORE_ID)
        types = [type(p) for p in result.promotions]
        self.assertIn(FlatOffPromotion, types)
        self.assertIn(PercentOffPromotion, types)
        self.assertIn(FreeDeliveryPromotion, types)

    # --- create() ---

    def test_create_returns_response_with_id(self):
        payload = PromotionsService_flat_off_helper()
        result = self.client.promotions.create(fixtures.STORE_ID, payload)
        self.assertIsInstance(result, CreatePromotionResponse)
        self.assertEqual(result.promotion_id, fixtures.PROMO_ID_NEW)

    # --- revoke() ---

    def test_revoke_returns_dict(self):
        result = self.client.promotions.revoke(fixtures.PROMO_ID_FLAT)
        self.assertIsInstance(result, dict)

    # --- static helper methods ---

    def test_flat_off_helper_builds_correct_payload(self):
        from api.services.promotions import PromotionsService
        payload = PromotionsService.flat_off(
            start_time="2026-03-01T00:00:00Z",
            end_time="2026-03-31T23:59:59Z",
            discount_amount=300,
            min_spend=1500,
            currency_code="EUR",
        )
        self.assertEqual(payload["promo_type"], "FLATOFF")
        self.assertEqual(payload["flat_off_discount"]["discount_value"]["amount"], 300)
        self.assertEqual(
            payload["flat_off_discount"]["min_basket_constraint"]["min_spend"]["amount"],
            1500,
        )

    def test_percent_off_helper_builds_correct_payload(self):
        from api.services.promotions import PromotionsService
        payload = PromotionsService.percent_off(
            start_time="2026-03-01T00:00:00Z",
            end_time="2026-03-31T23:59:59Z",
            percent_value=20,
            max_discount=500,
        )
        self.assertEqual(payload["promo_type"], "PERCENTOFF")
        self.assertEqual(payload["percent_off_discount"]["percent_value"], 20)

    def test_free_delivery_helper_builds_correct_payload(self):
        from api.services.promotions import PromotionsService
        payload = PromotionsService.free_delivery(
            start_time="2026-03-01T00:00:00Z",
            end_time="2026-03-31T23:59:59Z",
        )
        self.assertEqual(payload["promo_type"], "FREEDELIVERY")

    # --- repr ---

    def test_promotion_repr(self):
        result = self.client.promotions.get(fixtures.PROMO_ID_FLAT)
        self.assertIn(fixtures.PROMO_ID_FLAT, repr(result))


def PromotionsService_flat_off_helper() -> dict:
    """Helper local pour construire un payload FLATOFF sans importer le service."""
    from api.services.promotions import PromotionsService
    return PromotionsService.flat_off(
        start_time="2026-03-01T00:00:00Z",
        end_time="2026-03-31T23:59:59Z",
        discount_amount=300,
        min_spend=1500,
        currency_code="EUR",
    )


if __name__ == "__main__":
    unittest.main(verbosity=2)