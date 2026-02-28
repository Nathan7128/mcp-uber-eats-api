from __future__ import annotations

from enum import Enum
from typing import Optional, List

from api.models.common import UberEatsBaseModel, PaginationData


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class OnboardingStatus(str, Enum):
    ACTIVE = "ACTIVE"
    REMOVED = "REMOVED"
    PENDING = "PENDING"
    UNKNOWN = "UNKNOWN"


class StoreStatusEnum(str, Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"


class MerchantType(str, Enum):
    RESTAURANT = "MERCHANT_TYPE_RESTAURANT"
    GROCERY = "MERCHANT_TYPE_GROCERY"
    LIQUOR = "MERCHANT_TYPE_LIQUOR"
    SPECIALTY_FOOD = "MERCHANT_TYPE_SPECIALTY_FOOD"
    CONVENIENCE = "MERCHANT_TYPE_CONVENIENCE"
    PHARMACY = "MERCHANT_TYPE_PHARMACY"
    FLORIST = "MERCHANT_TYPE_FLORIST"
    PET_SUPPLY = "MERCHANT_TYPE_PET_SUPPLY"
    RETAIL = "MERCHANT_TYPE_RETAIL"
    VIRTUAL_RESTAURANT = "MERCHANT_TYPE_VIRTUAL_RESTAURANT"
    UNKNOWN = "MERCHANT_TYPE_UNKNOWN"


class DelayType(str, Enum):
    NORMAL = "NORMAL"
    BUSY = "BUSY"
    VERY_BUSY = "VERY_BUSY"


# ---------------------------------------------------------------------------
# Nested models
# ---------------------------------------------------------------------------

class Contact(UberEatsBaseModel):
    """Store contact information."""

    email: Optional[str] = None
    name: Optional[str] = None
    phone_number: Optional[str] = None


class Location(UberEatsBaseModel):
    """Physical address of the store."""

    latitude: Optional[str] = None
    longitude: Optional[str] = None
    street_address_line_one: Optional[str] = None
    street_address_line_two: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    unit_number: Optional[str] = None
    business_name: Optional[str] = None


class PreparationTimeDelayStatus(UberEatsBaseModel):
    """Current busy-mode delay applied to preparation time."""

    type: Optional[DelayType] = None
    is_active_until: Optional[str] = None
    delay_duration: Optional[int] = None  # seconds


class PrepDelay(UberEatsBaseModel):
    """Container for the current delay status and eligibility."""

    status: Optional[PreparationTimeDelayStatus] = None
    allowed: Optional[bool] = None


class PreparationTimes(UberEatsBaseModel):
    """Preparation time configuration for the store."""

    default_value: Optional[int] = None  # seconds
    delay: Optional[PrepDelay] = None


class OOIEligibility(UberEatsBaseModel):
    """Eligibility for the Out-Of-Item flow."""

    enabled: Optional[bool] = None
    not_eligible_reason: Optional[str] = None


class OOIConfig(UberEatsBaseModel):
    """Out-Of-Item configuration: how the store handles missing items."""

    is_substitute_item_enabled: Optional[bool] = None
    is_store_replace_item_enabled: Optional[bool] = None
    is_cancel_order_enabled: Optional[bool] = None
    is_remove_item_enabled: Optional[bool] = None
    ooi_eligibility: Optional[OOIEligibility] = None


class PriceAdjustmentConfig(UberEatsBaseModel):
    """Configuration for order price adjustments."""

    is_price_adjustment_enabled: Optional[bool] = None
    maximum_price_adjustment: Optional[float] = None  # amount_e5 format
    requires_tax_rate_for_adjustment: Optional[bool] = None
    is_tax_inclusive: Optional[bool] = None


class FulfillmentTypeAvailability(UberEatsBaseModel):
    """Which fulfillment types are active for this store."""

    DELIVERY_BY_UBER: Optional[bool] = None
    DELIVERY_BY_MERCHANT: Optional[bool] = None
    DINE_IN: Optional[bool] = None
    PICKUP: Optional[bool] = None


class UberMerchantTypeInfo(UberEatsBaseModel):
    """Uber's internal standardized category for this merchant."""

    type: Optional[MerchantType] = None


# ---------------------------------------------------------------------------
# Top-level response models
# ---------------------------------------------------------------------------

class Store(UberEatsBaseModel):
    """Full store object as returned by the Store API."""

    id: Optional[str] = None
    name: Optional[str] = None
    contact: Optional[Contact] = None
    location: Optional[Location] = None
    pickup_instructions: Optional[str] = None
    timezone: Optional[str] = None
    fulfillment_type_availability: Optional[FulfillmentTypeAvailability] = None
    prep_times: Optional[PreparationTimes] = None
    onboarding_status: Optional[OnboardingStatus] = None
    auto_accept: Optional[bool] = None
    ooi_config: Optional[OOIConfig] = None
    merchant_contact_emails: Optional[str] = None
    max_delivery_partners_allowed: Optional[float] = None
    support_number: Optional[str] = None
    adjustment_config: Optional[PriceAdjustmentConfig] = None
    uber_merchant_type: Optional[UberMerchantTypeInfo] = None

    def __repr__(self) -> str:
        return f"<Store id={self.id!r} name={self.name!r}>"


class StoreList(UberEatsBaseModel):
    """Paginated list of stores."""

    data: Optional[List[Store]] = None
    pagination_data: Optional[PaginationData] = None


class StoreStatusResponse(UberEatsBaseModel):
    """Current online/offline status of a store."""

    status: Optional[StoreStatusEnum] = None
    reason: Optional[str] = None
    is_offline_until: Optional[str] = None

    @property
    def is_online(self) -> bool:
        return self.status == StoreStatusEnum.ONLINE
