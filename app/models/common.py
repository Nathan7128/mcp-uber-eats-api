from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from typing import Optional

__all__ = ["UberEatsBaseModel", "CurrencyAmount", "Money", "PaginationData"]


class UberEatsBaseModel(BaseModel):
    """Base class for all Uber Eats API models.

    - extra fields are silently ignored (API may return undocumented fields)
    - field population by name is enabled
    """

    model_config = ConfigDict(extra="ignore", populate_by_name=True)


class CurrencyAmount(UberEatsBaseModel):
    """Monetary amount with currency and precision representation.

    amount_e5 is the amount multiplied by 10^5 for precision.
    e.g. $7.50 → amount_e5=750000
    """

    amount_e5: Optional[float] = None
    currency_code: Optional[str] = None
    formatted: Optional[str] = None

    @property
    def amount(self) -> Optional[float]:
        """Return the human-readable decimal amount (amount_e5 / 100_000)."""
        if self.amount_e5 is not None:
            return round(self.amount_e5 / 100_000, 5)
        return None


class Money(UberEatsBaseModel):
    """Full monetary representation of a charge, split into net, tax, and gross."""

    display_amount: Optional[str] = None
    net: Optional[CurrencyAmount] = None
    tax: Optional[CurrencyAmount] = None
    gross: Optional[CurrencyAmount] = None
    is_tax_inclusive: Optional[bool] = None


class PaginationData(UberEatsBaseModel):
    next_page_token: Optional[str] = None
    page_size: Optional[int] = None
