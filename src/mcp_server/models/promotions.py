from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

__all__ = ["PromotionModel", "PromotionListModel"]


class PromotionModel(BaseModel):
    """An Uber Eats promotional offer with type-specific discount details.

    Flattens nested API fields: promo_type → type,
    promotion_customization.user_group → target_customers,
    and selects the correct discount sub-object into discount_details.
    """

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    promotion_id: str | None = None
    store_id: str | None = None
    type: str | None = Field(None, alias="promo_type")
    state: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    currency_code: str | None = None
    target_customers: str | None = None
    discount_details: Any | None = None

    @model_validator(mode="before")
    @classmethod
    def extract_fields(cls, values: dict) -> dict:
        # Extract target customer group
        customization = values.get("promotion_customization") or {}
        if isinstance(customization, dict):
            values["target_customers"] = customization.get("user_group")

        # Extract type-specific discount details
        promo_type = values.get("promo_type")
        discount_key = {
            "FLATOFF": "flat_off_discount",
            "PERCENTOFF": "percent_off_discount",
            "BOGO": "bogo_discount",
            "FREEITEM_MINBASKET": "free_item_discount",
            "MENU_ITEM_DISCOUNT": "menu_item_discount",
        }.get(promo_type)
        if discount_key:
            values["discount_details"] = values.get(discount_key)

        return values


class PromotionListModel(BaseModel):
    """List of promotions for a store."""

    model_config = ConfigDict(extra="ignore")

    promotions: list[PromotionModel] | None = None
