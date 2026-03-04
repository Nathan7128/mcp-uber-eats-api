from __future__ import annotations
from typing import TYPE_CHECKING

from app.models.promotions import (
    BasePromotion,
    CreatePromotionResponse,
    PromotionList,
    parse_promotion,
)

if TYPE_CHECKING:
    from app.client import UberEatsClient


class PromotionsService:
    """Wrapper for the Uber Eats Marketplace Promotions API.

    Supports creating, reading, listing and revoking store promotions.

    Endpoints covered:
    - POST   /v1/delivery/stores/{store_id}/promotion      → create()
    - GET    /v1/delivery/promotions/{promotion_id}        → get()
    - DELETE /v1/delivery/promotions/{promotion_id}        → revoke()
    - GET    /v1/delivery/stores/{store_id}/promotions     → list()

    Promotion types: FLATOFF, FREEITEM_MINBASKET, BOGO, PERCENTOFF,
                     MENU_ITEM_DISCOUNT, FREEDELIVERY
    """

    def __init__(self, client: UberEatsClient):
        self._client = client

    # ------------------------------------------------------------------
    # POST /v1/delivery/stores/{store_id}/promotion
    # ------------------------------------------------------------------

    def create(self, store_id: str, promotion: dict) -> CreatePromotionResponse:
        """Create a promotion for a store.

        The promotion dict must include a "promo_type" field and the
        corresponding discount object. Common required fields:
            - promo_type (str): One of the types below.
            - start_time (str): RFC3339 start timestamp.
            - end_time (str): RFC3339 end timestamp.
            - currency_code (str): e.g. "USD".

        Promotion types and their required fields:

        FLATOFF:
            {
                "promo_type": "FLATOFF",
                "start_time": "2024-01-01T00:00:00Z",
                "end_time": "2024-01-31T23:59:59Z",
                "currency_code": "USD",
                "flat_off_discount": {
                    "min_basket_constraint": {"min_spend": {"amount": 1500}},
                    "discount_value": {"amount": 300}
                }
            }

        PERCENTOFF:
            {
                "promo_type": "PERCENTOFF",
                "percent_off_discount": {
                    "min_basket_constraint": {"min_spend": {"amount": 1000}},
                    "percent_value": 20,
                    "max_discount_value": {"amount": 500}
                }
            }

        BOGO:
            {
                "promo_type": "BOGO",
                "bogo_discount": {
                    "target_items": [{"item_external_id": "item-123"}]
                }
            }

        FREEITEM_MINBASKET:
            {
                "promo_type": "FREEITEM_MINBASKET",
                "free_item_discount": {
                    "min_basket_constraint": {"min_spend": {"amount": 2000}},
                    "free_items": [{"free_item_id": "item-456"}]
                }
            }

        MENU_ITEM_DISCOUNT:
            {
                "promo_type": "MENU_ITEM_DISCOUNT",
                "menu_item_discount": {
                    "item_discounts": [{
                        "item": {"item_external_id": "item-789"},
                        "discount_amount": {"percent_discount": {"percent_value": 15}}
                        # or: "discount_amount": {"fixed_discount": {"amount": 100}}
                    }]
                }
            }

        FREEDELIVERY:
            {
                "promo_type": "FREEDELIVERY",
                "start_time": "2024-01-01T00:00:00Z",
                "end_time": "2024-01-31T23:59:59Z"
            }

        Optional common fields:
            - external_promotion_id (str): Your internal reference ID.
            - user_group (str): "ALL_CUSTOMERS" or a specific segment.
            - allow_unlimited_apply (bool): Allow customers to use it multiple times.
            - budget (dict): e.g. {"unlimited": True} or
                             {"periodic_budget": {"period": "WEEKLY", "amount": 10000}}
            - promotion_customization (dict): e.g. {"marketing_experience_type": "HAPPY_HOUR"}

        Args:
            store_id: The Uber Eats store UUID.
            promotion: Promotion configuration dict (see above).

        Returns:
            CreatePromotionResponse with .promotion_id.
        """
        data = self._client.post(f"/v1/delivery/stores/{store_id}/promotion", json=promotion)
        return CreatePromotionResponse.model_validate(data)

    # ------------------------------------------------------------------
    # GET /v1/delivery/promotions/{promotion_id}
    # ------------------------------------------------------------------

    def get(self, promotion_id: str) -> BasePromotion:
        """Retrieve a specific promotion by ID.

        Args:
            promotion_id: The Uber Eats promotion UUID.

        Returns:
            Typed promotion object (FlatOffPromotion, PercentOffPromotion, etc.)
            based on the promo_type field in the response.
        """
        data = self._client.get(f"/v1/delivery/promotions/{promotion_id}")
        return parse_promotion(data)

    # ------------------------------------------------------------------
    # DELETE /v1/delivery/promotions/{promotion_id}
    # ------------------------------------------------------------------

    def revoke(self, promotion_id: str) -> dict:
        """Revoke (delete) an active promotion.

        Args:
            promotion_id: The Uber Eats promotion UUID.

        Returns:
            Empty dict on success.
        """
        return self._client.delete(f"/v1/delivery/promotions/{promotion_id}")

    # ------------------------------------------------------------------
    # GET /v1/delivery/stores/{store_id}/promotions
    # ------------------------------------------------------------------

    def list(self, store_id: str) -> PromotionList:
        """List all active promotions for a store.

        Args:
            store_id: The Uber Eats store UUID.

        Returns:
            PromotionList — each item in .promotions is typed
            (FlatOffPromotion, PercentOffPromotion, etc.).
        """
        data = self._client.get(f"/v1/delivery/stores/{store_id}/promotions")
        return PromotionList.model_validate(data)

    # ------------------------------------------------------------------
    # Convenience factory methods
    # ------------------------------------------------------------------

    @staticmethod
    def flat_off(
        start_time: str,
        end_time: str,
        discount_amount: int,
        min_spend: int = None,
        currency_code: str = "USD",
        **kwargs,
    ) -> dict:
        """Build a FLATOFF promotion payload.

        Args:
            start_time: RFC3339 start timestamp.
            end_time: RFC3339 end timestamp.
            discount_amount: Flat discount in minor currency units (e.g. 300 = $3.00).
            min_spend: Minimum basket amount to qualify, in minor units.
            currency_code: Currency code (default "USD").
            **kwargs: Additional promotion fields (external_promotion_id, budget, etc.).
        """
        promo = {
            "promo_type": "FLATOFF",
            "start_time": start_time,
            "end_time": end_time,
            "currency_code": currency_code,
            "flat_off_discount": {
                "discount_value": {"amount": discount_amount},
            },
            **kwargs,
        }
        if min_spend is not None:
            promo["flat_off_discount"]["min_basket_constraint"] = {
                "min_spend": {"amount": min_spend}
            }
        return promo

    @staticmethod
    def percent_off(
        start_time: str,
        end_time: str,
        percent_value: int,
        min_spend: int = None,
        max_discount: int = None,
        currency_code: str = "USD",
        **kwargs,
    ) -> dict:
        """Build a PERCENTOFF promotion payload.

        Args:
            start_time: RFC3339 start timestamp.
            end_time: RFC3339 end timestamp.
            percent_value: Percentage discount (e.g. 20 for 20% off).
            min_spend: Minimum basket in minor units.
            max_discount: Maximum discount cap in minor units.
            currency_code: Currency code (default "USD").
            **kwargs: Additional promotion fields.
        """
        discount = {"percent_value": percent_value}
        if min_spend is not None:
            discount["min_basket_constraint"] = {"min_spend": {"amount": min_spend}}
        if max_discount is not None:
            discount["max_discount_value"] = {"amount": max_discount}
        return {
            "promo_type": "PERCENTOFF",
            "start_time": start_time,
            "end_time": end_time,
            "currency_code": currency_code,
            "percent_off_discount": discount,
            **kwargs,
        }

    @staticmethod
    def free_delivery(start_time: str, end_time: str, **kwargs) -> dict:
        """Build a FREEDELIVERY promotion payload.

        Args:
            start_time: RFC3339 start timestamp.
            end_time: RFC3339 end timestamp.
            **kwargs: Additional promotion fields.
        """
        return {
            "promo_type": "FREEDELIVERY",
            "start_time": start_time,
            "end_time": end_time,
            **kwargs,
        }
