"""Modèles Pydantic pour les endpoints Promotions de l'API Uber Eats.

Rôle : normaliser les différents types de promotions (FLATOFF, PERCENTOFF, BOGO…)
en un modèle unifié avec un champ discount_details générique.
"""
from pydantic import BaseModel, ConfigDict, Field, model_validator

__all__ = ["PromotionModel", "PromotionListModel"]


class PromotionModel(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    promotion_id: str | None = None
    store_id: str | None = None
    type: str | None = Field(None, alias="promo_type")
    state: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    currency_code: str | None = None
    target_customers: str | None = None
    discount_details: dict | None = None

    @model_validator(mode="before")
    @classmethod
    def extract_fields(cls, values: dict) -> dict:
        # Cible clients : {"promotion_customization": {"user_group": "ALL_EATERS"}}
        customization = values.get("promotion_customization") or {}
        if isinstance(customization, dict):
            values["target_customers"] = customization.get("user_group")

        # Chaque type de promotion a son propre sous-objet de remise dans la réponse API ;
        # on le normalise dans discount_details pour simplifier la lecture par le LLM.
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

    promotions: list[PromotionModel] | None = None
