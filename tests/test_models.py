"""Unit tests for Pydantic models — validate field extraction and noise filtering."""
import pytest

from mcp_server.models.stores import StoreModel, StoreStatusModel, StoreListModel
from mcp_server.models.orders import OrderItemModel, OrderModel, OrderListModel
from mcp_server.models.promotions import PromotionModel, PromotionListModel
from tests.fixtures import (
    STORE_RAW,
    STORE_LIST_RAW,
    STORE_LIST_EMPTY_RAW,
    STORE_STATUS_ONLINE_RAW,
    STORE_STATUS_OFFLINE_RAW,
    ORDER_ITEM_RAW,
    ORDER_ITEM_SIMPLE_RAW,
    _order_inner,
    ORDER_LIST_RAW,
    PROMOTION_PERCENTOFF_RAW,
    PROMOTION_FLATOFF_RAW,
    PROMOTION_LIST_RAW,
)


# ──────────────────────────────────────────────────────────────────────────────
# StoreModel
# ──────────────────────────────────────────────────────────────────────────────

class TestStoreModel:
    def setup_method(self):
        self.store = StoreModel.model_validate(STORE_RAW)
        self.dump = self.store.model_dump(exclude_none=True)

    def test_basic_fields(self):
        assert self.store.name == "Le Bistro du Coin"
        assert self.store.timezone == "Europe/Paris"
        assert self.store.onboarding_status == "ONBOARDED"
        assert self.store.auto_accept is False

    def test_location_extracted_as_address(self):
        """'location' from the API is remapped to 'address'."""
        assert self.store.address is not None
        assert self.store.address.street == "12 rue de la Paix"
        assert self.store.address.city == "Paris"
        assert self.store.address.country == "FR"
        assert self.store.address.postal_code == "75001"

    def test_prep_time_extracted(self):
        """prep_time_seconds is extracted from nested prep_times.default_value."""
        assert self.store.prep_time_seconds == 900

    def test_merchant_type_extracted(self):
        """merchant_type is extracted from uber_merchant_type.type."""
        assert self.store.merchant_type == "RESTAURANT"

    def test_contact_fields(self):
        assert self.store.contact is not None
        assert self.store.contact.name == "Jean Dupont"
        assert self.store.contact.email == "jean@bistro.fr"
        assert self.store.contact.phone == "+33612345678"

    def test_api_noise_filtered(self):
        """Extra API fields (posId, merchantUUID…) must not appear in the dump."""
        assert "posId" not in self.dump
        assert "merchantUUID" not in self.dump
        assert "location" not in self.dump
        assert "prep_times" not in self.dump
        assert "uber_merchant_type" not in self.dump

    def test_dump_keys_are_llm_friendly(self):
        """The dump should have readable, descriptive keys — no raw API noise."""
        expected_keys = {"name", "timezone", "onboarding_status", "auto_accept",
                         "address", "contact", "prep_time_seconds", "merchant_type"}
        assert expected_keys.issubset(self.dump.keys())


# ──────────────────────────────────────────────────────────────────────────────
# StoreStatusModel
# ──────────────────────────────────────────────────────────────────────────────

class TestStoreStatusModel:
    def test_online_status(self):
        model = StoreStatusModel.model_validate(STORE_STATUS_ONLINE_RAW)
        dump = model.model_dump(exclude_none=True)
        assert model.status == "ONLINE"
        assert model.is_online is True
        assert "offline_reason" not in dump
        assert "offline_until" not in dump

    def test_offline_status(self):
        model = StoreStatusModel.model_validate(STORE_STATUS_OFFLINE_RAW)
        dump = model.model_dump(exclude_none=True)
        assert model.status == "OFFLINE"
        assert model.is_online is False
        assert model.offline_reason == "CLOSED"
        assert model.offline_until == "2026-03-15T18:00:00Z"
        assert "reason" not in dump
        assert "is_offline_until" not in dump

    def test_is_online_is_bool(self):
        online = StoreStatusModel.model_validate(STORE_STATUS_ONLINE_RAW)
        offline = StoreStatusModel.model_validate(STORE_STATUS_OFFLINE_RAW)
        assert isinstance(online.is_online, bool)
        assert isinstance(offline.is_online, bool)


# ──────────────────────────────────────────────────────────────────────────────
# StoreListModel
# ──────────────────────────────────────────────────────────────────────────────

class TestStoreListModel:
    def test_stores_extracted_from_data(self):
        model = StoreListModel.model_validate(STORE_LIST_RAW)
        assert model.stores is not None
        assert len(model.stores) == 1
        assert model.stores[0].name == "Le Bistro du Coin"

    def test_pagination_token_extracted(self):
        model = StoreListModel.model_validate(STORE_LIST_RAW)
        assert model.next_page_token == "tok-page-2"

    def test_empty_list(self):
        model = StoreListModel.model_validate(STORE_LIST_EMPTY_RAW)
        dump = model.model_dump(exclude_none=True)
        assert dump.get("stores") is None or dump.get("stores") == []

    def test_dump_has_no_raw_data_key(self):
        dump = StoreListModel.model_validate(STORE_LIST_RAW).model_dump(exclude_none=True)
        assert "data" not in dump


# ──────────────────────────────────────────────────────────────────────────────
# OrderItemModel
# ──────────────────────────────────────────────────────────────────────────────

class TestOrderItemModel:
    def test_title_mapped_to_name(self):
        item = OrderItemModel.model_validate(ORDER_ITEM_RAW)
        assert item.name == "Burger Classique"

    def test_quantity_extracted_from_nested_object(self):
        item = OrderItemModel.model_validate(ORDER_ITEM_RAW)
        assert item.quantity == 2

    def test_special_instructions_extracted(self):
        item = OrderItemModel.model_validate(ORDER_ITEM_RAW)
        assert item.special_instructions == "Sans oignon"

    def test_modifiers_extracted(self):
        item = OrderItemModel.model_validate(ORDER_ITEM_RAW)
        assert item.modifiers is not None
        assert len(item.modifiers) == 1
        assert item.modifiers[0].group == "Cuisson"
        assert item.modifiers[0].options == ["À point"]

    def test_simple_item_no_modifiers(self):
        item = OrderItemModel.model_validate(ORDER_ITEM_SIMPLE_RAW)
        dump = item.model_dump(exclude_none=True)
        assert item.name == "Frites"
        assert item.quantity == 1
        assert "modifiers" not in dump
        assert "special_instructions" not in dump


# ──────────────────────────────────────────────────────────────────────────────
# OrderModel
# ──────────────────────────────────────────────────────────────────────────────

class TestOrderModel:
    def setup_method(self):
        self.order = OrderModel.model_validate(_order_inner())
        self.dump = self.order.model_dump(exclude_none=True)

    def test_basic_fields(self):
        assert self.order.id == "order-xyz-456"
        assert self.order.display_id == "#1234"
        assert self.order.state == "ACCEPTED"
        assert self.order.status == "ACTIVE"
        assert self.order.fulfillment_type == "DELIVERY"

    def test_customer_extracted(self):
        assert self.order.customer_name == "Marie Martin"
        assert self.order.customer_phone == "+33687654321"

    def test_items_flattened_from_carts(self):
        assert self.order.items is not None
        assert len(self.order.items) == 2
        assert self.order.items[0].name == "Burger Classique"
        assert self.order.items[1].name == "Frites"

    def test_item_count_computed(self):
        # 2 burgers + 1 frites = 3
        assert self.order.item_count == 3

    def test_delivery_status_extracted(self):
        assert self.order.delivery_status == "COURIER_ASSIGNED"

    def test_store_instructions(self):
        assert self.order.store_instructions == "Sonner à l'interphone"

    def test_api_noise_filtered(self):
        assert "customers" not in self.dump
        assert "carts" not in self.dump
        assert "deliveries" not in self.dump


# ──────────────────────────────────────────────────────────────────────────────
# OrderListModel
# ──────────────────────────────────────────────────────────────────────────────

class TestOrderListModel:
    def setup_method(self):
        self.model = OrderListModel.model_validate(ORDER_LIST_RAW)
        self.dump = self.model.model_dump(exclude_none=True)

    def test_orders_unwrapped(self):
        """Each {"order": {...}} wrapper is unwrapped."""
        assert self.model.orders is not None
        assert len(self.model.orders) == 2

    def test_orders_are_parsed(self):
        assert self.model.orders[0].id == "order-xyz-456"
        assert self.model.orders[1].id == "order-xyz-789"

    def test_pagination_extracted(self):
        assert self.model.total_count == 2

    def test_dump_has_no_raw_data_key(self):
        assert "data" not in self.dump


# ──────────────────────────────────────────────────────────────────────────────
# PromotionModel
# ──────────────────────────────────────────────────────────────────────────────

class TestPromotionModel:
    def test_percentoff_discount_details(self):
        model = PromotionModel.model_validate(PROMOTION_PERCENTOFF_RAW)
        assert model.type == "PERCENTOFF"
        assert model.target_customers == "ALL_EATERS"
        assert model.discount_details is not None
        assert model.discount_details["discount_percentage"] == 20
        # Other discount keys must not appear
        dump = model.model_dump(exclude_none=True)
        assert "flat_off_discount" not in dump
        assert "bogo_discount" not in dump

    def test_flatoff_discount_details(self):
        model = PromotionModel.model_validate(PROMOTION_FLATOFF_RAW)
        assert model.type == "FLATOFF"
        assert model.target_customers == "NEW_EATERS"
        assert model.discount_details is not None
        assert model.discount_details["discount_value"] == 300

    def test_promotion_base_fields(self):
        model = PromotionModel.model_validate(PROMOTION_PERCENTOFF_RAW)
        assert model.promotion_id == "promo-001"
        assert model.store_id == "store-abc-123"
        assert model.state == "ACTIVE"
        assert model.currency_code == "EUR"

    def test_promo_type_alias(self):
        """promo_type from the API is exposed as 'type'."""
        dump = PromotionModel.model_validate(PROMOTION_PERCENTOFF_RAW).model_dump(exclude_none=True)
        assert "type" in dump
        assert "promo_type" not in dump


# ──────────────────────────────────────────────────────────────────────────────
# PromotionListModel
# ──────────────────────────────────────────────────────────────────────────────

class TestPromotionListModel:
    def test_promotions_parsed(self):
        model = PromotionListModel.model_validate(PROMOTION_LIST_RAW)
        assert model.promotions is not None
        assert len(model.promotions) == 2
        assert model.promotions[0].promotion_id == "promo-001"
        assert model.promotions[1].promotion_id == "promo-002"
