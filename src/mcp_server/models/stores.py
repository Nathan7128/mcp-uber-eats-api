from __future__ import annotations

from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, model_validator

__all__ = ["StoreModel", "StoreStatusModel", "StoreListModel"]


class ContactModel(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = Field(None, alias="phone_number")


class AddressModel(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    street: Optional[str] = Field(None, alias="street_address_line_one")
    city: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None


class StoreModel(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: Optional[str] = None
    name: Optional[str] = None
    contact: Optional[ContactModel] = None
    address: Optional[AddressModel] = None
    timezone: Optional[str] = None
    onboarding_status: Optional[str] = None
    auto_accept: Optional[bool] = None
    prep_time_seconds: Optional[int] = None
    merchant_type: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def extract_fields(cls, values: dict) -> dict:
        # Map location → address
        if "location" in values and "address" not in values:
            values["address"] = values["location"]

        # Extract prep time
        prep_times = values.get("prep_times") or {}
        if isinstance(prep_times, dict):
            values["prep_time_seconds"] = prep_times.get("default_value")

        # Extract merchant type
        merchant_type_obj = values.get("uber_merchant_type") or {}
        if isinstance(merchant_type_obj, dict):
            values["merchant_type"] = merchant_type_obj.get("type")

        return values


class StoreStatusModel(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    status: Optional[str] = None
    is_online: Optional[bool] = None
    offline_reason: Optional[str] = None
    offline_until: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def extract_fields(cls, values: dict) -> dict:
        values["is_online"] = values.get("status") == "ONLINE"
        values["offline_reason"] = values.get("reason")
        values["offline_until"] = values.get("is_offline_until")
        return values


class StoreListModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    stores: Optional[List[StoreModel]] = None
    next_page_token: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def extract_fields(cls, values: dict) -> dict:
        if "data" in values and "stores" not in values:
            values["stores"] = values["data"]

        pagination = values.get("pagination_data") or {}
        if isinstance(pagination, dict):
            values["next_page_token"] = pagination.get("next_page_token")

        return values
