from __future__ import annotations

from enum import Enum
from typing import Optional, List, Any

from pydantic import model_validator

from api.models.common import UberEatsBaseModel, Money


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class PromoType(str, Enum):
    FLATOFF = "FLATOFF"
    FREEITEM_MINBASKET = "FREEITEM_MINBASKET"
    BOGO = "BOGO"
    PERCENTOFF = "PERCENTOFF"
    MENU_ITEM_DISCOUNT = "MENU_ITEM_DISCOUNT"
    FREEDELIVERY = "FREEDELIVERY"


class PromotionState(str, Enum):
    ACTIVE = "active"
    PENDING = "pending"
    COMPLETED = "completed"
    REVOKED = "revoked"
    EXPIRED = "expired"
    DELETED = "deleted"


class UserGroup(str, Enum):
    ALL_CUSTOMERS = "ALL_CUSTOMERS"
    FIRST_TIME_CUSTOMERS = "FIRST_TIME_CUSTOMERS"


class DayOfWeek(str, Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


class BudgetPeriod(str, Enum):
    WEEKLY = "WEEKLY"
    DAILY = "DAILY"
    MONTHLY = "MONTHLY"


# ---------------------------------------------------------------------------
# Shared sub-models
# ---------------------------------------------------------------------------

class TimeRange(UberEatsBaseModel):
    start_time: Optional[str] = None
    end_time: Optional[str] = None


class DaypartConstraint(UberEatsBaseModel):
    """Limits a promotion to specific days and time windows."""

    days_of_week: Optional[List[DayOfWeek]] = None
    time_range: Optional[TimeRange] = None


class Budget(UberEatsBaseModel):
    """Spending cap for a promotion, optionally scoped to a period."""

    max_budget: Optional[Money] = None
    budget_period: Optional[BudgetPeriod] = None


class PromotionCustomization(UberEatsBaseModel):
    """Optional targeting / scheduling settings for a promotion."""

    daypart_constraints: Optional[List[DaypartConstraint]] = None
    user_group: Optional[UserGroup] = None
    engagement_campaign_type: Optional[str] = None  # e.g. "HAPPY_HOUR"


class MinBasketConstraint(UberEatsBaseModel):
    """Minimum cart value required to unlock the promotion."""

    min_spend: Optional[dict] = None  # {"amount": int}


# ---------------------------------------------------------------------------
# Discount sub-models (one per promotion type)
# ---------------------------------------------------------------------------

class FlatOffDiscount(UberEatsBaseModel):
    """Flat-amount discount: "Spend $X, Save $Y"."""

    min_basket_constraint: Optional[MinBasketConstraint] = None
    discount_value: Optional[Money] = None  # used in responses
    discount_amount: Optional[Money] = None  # alternate field name in some responses


class PercentOffDiscount(UberEatsBaseModel):
    """Percentage discount: "Get N% off (up to $X)"."""

    min_basket_constraint: Optional[MinBasketConstraint] = None
    percent_value: Optional[float] = None
    max_discount_value: Optional[Money] = None


class BOGODiscount(UberEatsBaseModel):
    """Buy-one-get-one: apply to specific target items."""

    target_items: Optional[List[dict]] = None  # [{"item_external_id": str}]


class FreeItemDiscount(UberEatsBaseModel):
    """Free item with minimum basket: "Spend $X, get [item] free"."""

    min_basket_constraint: Optional[MinBasketConstraint] = None
    free_items: Optional[List[dict]] = None  # [{"free_item_id": str}]


class ItemDiscount(UberEatsBaseModel):
    """Per-item discount entry for MENU_ITEM_DISCOUNT promotions."""

    item: Optional[dict] = None           # {"item_external_id": str}
    discount_amount: Optional[dict] = None  # {"percent_discount": {...}} or {"fixed_discount": {...}}


class MenuItemDiscount(UberEatsBaseModel):
    """Item-level discounts applied to specific menu items."""

    item_discounts: Optional[List[ItemDiscount]] = None


# ---------------------------------------------------------------------------
# Promotion response models
# ---------------------------------------------------------------------------

class BasePromotion(UberEatsBaseModel):
    """Fields common to every promotion type."""

    promotion_id: Optional[str] = None
    store_id: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    created_time: Optional[str] = None
    state: Optional[PromotionState] = None
    external_promotion_id: Optional[str] = None
    allow_unlimited_apply: Optional[bool] = None
    currency_code: Optional[str] = None
    budget: Optional[Budget] = None
    promo_type: Optional[PromoType] = None
    promotion_customization: Optional[PromotionCustomization] = None

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} id={self.promotion_id!r} "
            f"type={self.promo_type!r} state={self.state!r}>"
        )


class FlatOffPromotion(BasePromotion):
    """Flat-amount discount promotion."""

    promo_type: PromoType = PromoType.FLATOFF
    flat_off_discount: Optional[FlatOffDiscount] = None


class PercentOffPromotion(BasePromotion):
    """Percentage discount promotion."""

    promo_type: PromoType = PromoType.PERCENTOFF
    percent_off_discount: Optional[PercentOffDiscount] = None


class BOGOPromotion(BasePromotion):
    """Buy-one-get-one promotion."""

    promo_type: PromoType = PromoType.BOGO
    bogo_discount: Optional[BOGODiscount] = None


class FreeItemPromotion(BasePromotion):
    """Free item with minimum basket promotion."""

    promo_type: PromoType = PromoType.FREEITEM_MINBASKET
    free_item_discount: Optional[FreeItemDiscount] = None


class FreeDeliveryPromotion(BasePromotion):
    """Free delivery promotion."""

    promo_type: PromoType = PromoType.FREEDELIVERY


class MenuItemDiscountPromotion(BasePromotion):
    """Per-item discount promotion."""

    promo_type: PromoType = PromoType.MENU_ITEM_DISCOUNT
    menu_item_discount: Optional[MenuItemDiscount] = None


# ---------------------------------------------------------------------------
# Promotion factory
# ---------------------------------------------------------------------------

_PROMO_MODEL_MAP: dict[str, type[BasePromotion]] = {
    PromoType.FLATOFF: FlatOffPromotion,
    PromoType.PERCENTOFF: PercentOffPromotion,
    PromoType.BOGO: BOGOPromotion,
    PromoType.FREEITEM_MINBASKET: FreeItemPromotion,
    PromoType.FREEDELIVERY: FreeDeliveryPromotion,
    PromoType.MENU_ITEM_DISCOUNT: MenuItemDiscountPromotion,
}


def parse_promotion(data: dict) -> BasePromotion:
    """Deserialize a raw promotion dict into the appropriate typed model.

    Falls back to BasePromotion for unknown promo_type values.
    """
    promo_type = data.get("promo_type")
    model_cls = _PROMO_MODEL_MAP.get(promo_type, BasePromotion)
    return model_cls.model_validate(data)


# ---------------------------------------------------------------------------
# List / create response wrappers
# ---------------------------------------------------------------------------

class CreatePromotionResponse(UberEatsBaseModel):
    """Response from POST /v1/delivery/stores/{store_id}/promotion."""

    promotion_id: Optional[str] = None


class PromotionList(UberEatsBaseModel):
    """Response from GET /v1/delivery/stores/{store_id}/promotions."""

    promotions: Optional[List[Any]] = None

    @model_validator(mode="before")
    @classmethod
    def _parse_promotions(cls, values: dict) -> dict:
        raw = values.get("promotions")
        if isinstance(raw, list):
            values["promotions"] = [
                parse_promotion(p) if isinstance(p, dict) else p
                for p in raw
            ]
        return values
