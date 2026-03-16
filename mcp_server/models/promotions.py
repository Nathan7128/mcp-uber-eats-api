from __future__ import annotations

from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict, Field, model_validator

__all__ = ["PromotionModel", "PromotionListModel"]


class PromotionModel(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    promotion_id: Optional[str] = None
    store_id: Optional[str] = None
    type: Optional[str] = Field(None, alias="promo_type")
    state: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    currency_code: Optional[str] = None
    target_customers: Optional[str] = None
    discount_details: Optional[Any] = None

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
    model_config = ConfigDict(extra="ignore")

    promotions: Optional[List[PromotionModel]] = None
