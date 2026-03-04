from __future__ import annotations

from enum import Enum
from typing import Any, Optional, List

from app.models.common import UberEatsBaseModel, Money, PaginationData

__all__ = [
    "OrderState", "OrderStatus", "PreparationStatus", "FulfillmentType",
    "OrderingPlatform", "DeliveryStatus", "InteractionType",
    "CustomerName", "OrderHistory", "Phone", "CustomerContact", "Customer",
    "GeoPoint", "Vehicle", "DeliveryPartner", "Delivery",
    "CustomerRequest", "ItemQuantity", "ModifierOption", "ModifierGroup",
    "OrderItem", "CartCharges", "Cart", "OrderStoreInfo",
    "Order", "RestaurantOrder", "OrderList", "AdjustPriceResponse",
]


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class OrderState(str, Enum):
    CREATED = "CREATED"
    OFFERED = "OFFERED"
    ACCEPTED = "ACCEPTED"
    HANDED_OFF = "HANDED_OFF"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


class OrderStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    UNKNOWN = "UNKNOWN"


class PreparationStatus(str, Enum):
    PREPARING = "PREPARING"
    OUT_OF_ITEM_PENDING_CUSTOMER_RESPONSE = "OUT_OF_ITEM_PENDING_CUSTOMER_RESPONSE"
    READY_FOR_HANDOFF = "READY_FOR_HANDOFF"


class FulfillmentType(str, Enum):
    DELIVERY_BY_UBER = "DELIVERY_BY_UBER"
    DELIVERY_BY_MERCHANT = "DELIVERY_BY_MERCHANT"
    DINE_IN = "DINE_IN"
    PICKUP = "PICKUP"


class OrderingPlatform(str, Enum):
    UBER_EATS = "UBER_EATS"
    POSTMATES = "POSTMATES"


class DeliveryStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    EN_ROUTE_TO_PICKUP = "EN_ROUTE_TO_PICKUP"
    ARRIVED_AT_PICKUP = "ARRIVED_AT_PICKUP"
    EN_ROUTE_TO_DROPOFF = "EN_ROUTE_TO_DROPOFF"
    ARRIVED_AT_DROPOFF = "ARRIVED_AT_DROPOFF"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class InteractionType(str, Enum):
    DOOR_TO_DOOR = "DOOR_TO_DOOR"
    CURBSIDE = "CURBSIDE"
    LEAVE_AT_DOOR = "LEAVE_AT_DOOR"
    DELIVER_TO_DOOR = "DELIVER_TO_DOOR"


# ---------------------------------------------------------------------------
# Customer models
# ---------------------------------------------------------------------------

class CustomerName(UberEatsBaseModel):
    display_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    def __str__(self) -> str:
        return self.display_name or f"{self.first_name or ''} {self.last_name or ''}".strip()


class OrderHistory(UberEatsBaseModel):
    past_order_count: Optional[int] = None


class Phone(UberEatsBaseModel):
    number: Optional[str] = None
    country_code: Optional[str] = None


class CustomerContact(UberEatsBaseModel):
    phone: Optional[Phone] = None


class Customer(UberEatsBaseModel):
    """Customer associated with an order."""

    id: Optional[str] = None
    name: Optional[CustomerName] = None
    order_history: Optional[OrderHistory] = None
    contact: Optional[CustomerContact] = None
    is_primary_customer: Optional[bool] = None
    can_respond_to_fulfillment_issues: Optional[bool] = None

    def __repr__(self) -> str:
        return f"<Customer id={self.id!r} name={self.name!r}>"


# ---------------------------------------------------------------------------
# Delivery models
# ---------------------------------------------------------------------------

class GeoPoint(UberEatsBaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class Vehicle(UberEatsBaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    license_plate: Optional[str] = None


class DeliveryPartnerName(UberEatsBaseModel):
    display_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class DeliveryPartner(UberEatsBaseModel):
    """Courier assigned to a delivery."""

    id: Optional[str] = None
    name: Optional[DeliveryPartnerName] = None
    vehicle: Optional[Vehicle] = None
    picture_url: Optional[str] = None
    current_location: Optional[GeoPoint] = None

    def __repr__(self) -> str:
        return f"<DeliveryPartner id={self.id!r} name={self.name!r}>"


class Delivery(UberEatsBaseModel):
    """A single delivery leg for an order."""

    id: Optional[str] = None
    delivery_partner: Optional[DeliveryPartner] = None
    status: Optional[DeliveryStatus] = None
    location: Optional[GeoPoint] = None
    estimated_pick_up_time: Optional[str] = None
    estimated_dropoff_time: Optional[str] = None
    interaction_type: Optional[InteractionType] = None
    instructions: Optional[str] = None

    def __repr__(self) -> str:
        return f"<Delivery id={self.id!r} status={self.status!r}>"


# ---------------------------------------------------------------------------
# Cart / Item models
# ---------------------------------------------------------------------------

class CustomerRequest(UberEatsBaseModel):
    """Customer notes attached to an item."""

    allergy: Optional[str] = None
    special_instructions: Optional[str] = None


class ItemQuantity(UberEatsBaseModel):
    """Quantity expressed in sellable and priceable units."""

    amount: Optional[float] = None
    in_sellable_unit: Optional[float] = None
    in_priceable_unit: Optional[float] = None


class ModifierOption(UberEatsBaseModel):
    """A single selected option within a modifier group."""

    id: Optional[str] = None
    title: Optional[str] = None
    external_data: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[Money] = None


class ModifierGroup(UberEatsBaseModel):
    """A modifier group with its selected options (e.g. "Add-ons", "Size")."""

    id: Optional[str] = None
    title: Optional[str] = None
    external_data: Optional[str] = None
    selected_items: Optional[List[ModifierOption]] = None


class OrderItem(UberEatsBaseModel):
    """A line item inside a shopping cart."""

    id: Optional[str] = None
    cart_item_id: Optional[str] = None
    customer_id: Optional[str] = None
    title: Optional[str] = None
    external_data: Optional[str] = None
    quantity: Optional[ItemQuantity] = None
    default_quantity: Optional[ItemQuantity] = None
    customer_request: Optional[CustomerRequest] = None
    selected_modifier_groups: Optional[List[ModifierGroup]] = None
    picture_url: Optional[str] = None
    fulfillment_action: Optional[Any] = None

    def __repr__(self) -> str:
        qty = self.quantity.amount if self.quantity else None
        return f"<OrderItem id={self.id!r} title={self.title!r} qty={qty}>"


class CartCharges(UberEatsBaseModel):
    """Charge summaries for a shopping cart."""

    item_charge_summary: Optional[Money] = None
    merchant_fee_summary: Optional[Money] = None
    merchant_tip_summary: Optional[Money] = None


class Cart(UberEatsBaseModel):
    """Shopping cart containing items and charge breakdown."""

    id: Optional[str] = None
    items: Optional[List[OrderItem]] = None
    special_instructions: Optional[str] = None
    fulfillment_issues: Optional[List[Any]] = None

    def __repr__(self) -> str:
        count = len(self.items) if self.items else 0
        return f"<Cart id={self.id!r} items={count}>"


# ---------------------------------------------------------------------------
# Order store info (simplified — different from the full Store object)
# ---------------------------------------------------------------------------

class OrderStoreInfo(UberEatsBaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    external_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Order models
# ---------------------------------------------------------------------------

class Order(UberEatsBaseModel):
    """Core order data, shared between restaurant and retail orders."""

    id: Optional[str] = None
    display_id: Optional[str] = None
    external_id: Optional[str] = None
    state: Optional[OrderState] = None
    status: Optional[OrderStatus] = None
    preparation_status: Optional[PreparationStatus] = None
    ordering_platform: Optional[OrderingPlatform] = None
    fulfillment_type: Optional[FulfillmentType] = None
    store: Optional[OrderStoreInfo] = None
    customers: Optional[List[Customer]] = None
    deliveries: Optional[List[Delivery]] = None
    carts: Optional[List[Cart]] = None
    payment: Optional[Any] = None
    ready_for_pickup_time: Optional[str] = None
    created_time: Optional[str] = None
    completed_time: Optional[str] = None
    store_instructions: Optional[str] = None
    is_order_accuracy_risk: Optional[bool] = None
    has_membership_pass: Optional[bool] = None

    @property
    def primary_customer(self) -> Optional[Customer]:
        """Return the primary customer of the order."""
        if not self.customers:
            return None
        for c in self.customers:
            if c.is_primary_customer:
                return c
        return self.customers[0] if self.customers else None

    @property
    def item_count(self) -> int:
        """Total number of items across all carts."""
        if not self.carts:
            return 0
        return sum(
            int(item.quantity.amount or 0)
            for cart in self.carts
            for item in (cart.items or [])
            if item.quantity
        )

    def __repr__(self) -> str:
        return (
            f"<Order id={self.id!r} display_id={self.display_id!r} "
            f"state={self.state!r} status={self.status!r}>"
        )


class RestaurantOrder(UberEatsBaseModel):
    """Top-level wrapper returned by GET /v1/delivery/order/{order_id} for restaurants."""

    order: Optional[Order] = None

    def __repr__(self) -> str:
        return f"<RestaurantOrder {self.order!r}>"


class OrderList(UberEatsBaseModel):
    """Paginated list of orders returned by GET /v1/delivery/store/{store_id}/orders."""

    data: Optional[List[RestaurantOrder]] = None
    pagination_data: Optional[PaginationData] = None

    @property
    def orders(self) -> List[Order]:
        """Convenience accessor: unwrap the inner Order objects from the list."""
        if not self.data:
            return []
        return [ro.order for ro in self.data if ro.order is not None]


# ---------------------------------------------------------------------------
# Action response models
# ---------------------------------------------------------------------------

class AdjustPriceResponse(UberEatsBaseModel):
    tax_rate_applied: Optional[bool] = None
