from pydantic import BaseModel, ConfigDict, Field, model_validator

__all__ = ["StoreModel", "StoreStatusModel", "StoreListModel"]


class ContactModel(BaseModel):
    """Store owner contact information."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    name: str | None = None
    email: str | None = None
    phone: str | None = Field(None, alias="phone_number")


class AddressModel(BaseModel):
    """Physical address of a store."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    street: str | None = Field(None, alias="street_address_line_one")
    city: str | None = None
    country: str | None = None
    postal_code: str | None = None


class StoreModel(BaseModel):
    """Filtered representation of an Uber Eats store.

    Flattens nested API fields: location → address,
    prep_times.default_value → prep_time_seconds,
    uber_merchant_type.type → merchant_type.
    """

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
    """Online/offline status of a store."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    status: str | None = None
    is_online: bool | None = None
    offline_reason: str | None = None
    offline_until: str | None = None

    @model_validator(mode="before")
    @classmethod
    def extract_fields(cls, values: dict) -> dict:
        values["is_online"] = values.get("status") == "ONLINE"
        values["offline_reason"] = values.get("reason")
        values["offline_until"] = values.get("is_offline_until")
        return values


class StoreListModel(BaseModel):
    """Paginated list of stores."""

    model_config = ConfigDict(extra="ignore")

    stores: list[StoreModel] | None = None
    next_page_token: str | None = None

    @model_validator(mode="before")
    @classmethod
    def extract_fields(cls, values: dict) -> dict:
        if "data" in values and "stores" not in values:
            values["stores"] = values["data"]

        pagination = values.get("pagination_data") or {}
        if isinstance(pagination, dict):
            values["next_page_token"] = pagination.get("next_page_token")

        return values
