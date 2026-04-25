"""Modèles Pydantic pour les endpoints Store de l'API Uber Eats.

Rôle : recevoir la réponse brute de l'API, aplatir les structures imbriquées,
et ne conserver que les champs utiles au LLM via model_dump(exclude_none=True).
"""
from pydantic import BaseModel, ConfigDict, Field, model_validator

__all__ = ["StoreModel", "StoreStatusModel", "StoreListModel"]


class ContactModel(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    name: str | None = None
    email: str | None = None
    phone: str | None = Field(None, alias="phone_number")


class AddressModel(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    street: str | None = Field(None, alias="street_address_line_one")
    city: str | None = None
    country: str | None = None
    postal_code: str | None = None


class StoreModel(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str | None = None
    name: str | None = None
    contact: ContactModel | None = None
    address: AddressModel | None = None
    timezone: str | None = None
    onboarding_status: str | None = None
    auto_accept: bool | None = None
    prep_time_seconds: int | None = None
    merchant_type: str | None = None

    @model_validator(mode="before")
    @classmethod
    def extract_fields(cls, values: dict) -> dict:
        # Certains endpoints retournent "store_id" au lieu de "id"
        if "store_id" in values and "id" not in values:
            values["id"] = values["store_id"]

        # L'adresse est imbriquée sous "location" dans la réponse API
        if "location" in values and "address" not in values:
            values["address"] = values["location"]

        # Temps de préparation : {"prep_times": {"default_value": 900}}
        prep_times = values.get("prep_times") or {}
        if isinstance(prep_times, dict):
            values["prep_time_seconds"] = prep_times.get("default_value")

        # Type de commerce : {"uber_merchant_type": {"type": "RESTAURANT"}}
        merchant_type_obj = values.get("uber_merchant_type") or {}
        if isinstance(merchant_type_obj, dict):
            values["merchant_type"] = merchant_type_obj.get("type")

        return values


class StoreStatusModel(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    status: str | None = None
    is_online: bool | None = None
    offline_reason: str | None = None
    offline_until: str | None = None

    @model_validator(mode="before")
    @classmethod
    def extract_fields(cls, values: dict) -> dict:
        # Calcul du booléen is_online à partir du champ status
        values["is_online"] = values.get("status") == "ONLINE"
        # Renommage des champs pour plus de clarté côté LLM
        values["offline_reason"] = values.get("reason")
        values["offline_until"] = values.get("is_offline_until")
        return values


class StoreListModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    stores: list[StoreModel] | None = None
    next_page_token: str | None = None

    @model_validator(mode="before")
    @classmethod
    def extract_fields(cls, values: dict) -> dict:
        # L'API retourne la liste sous "data", on la remonte sous "stores"
        if "data" in values and "stores" not in values:
            values["stores"] = values["data"]

        # Pagination : {"pagination_data": {"next_page_token": "..."}}
        pagination = values.get("pagination_data") or {}
        if isinstance(pagination, dict):
            values["next_page_token"] = pagination.get("next_page_token")

        return values
