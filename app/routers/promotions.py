from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.client import UberEatsClient
from app.models.promotions import BasePromotion, PromotionList
from app.dependencies import get_client

router = APIRouter(tags=["Promotions"])


@router.get(
    "/promotions/{promotion_id}",
    response_model=BasePromotion,
    summary="Get a promotion by ID",
    description=(
        "Retrieve details for a specific promotion by its UUID. "
        "The response is typed according to the promo_type field: "
        "FlatOffPromotion, PercentOffPromotion, FreeDeliveryPromotion, etc. "
        "Promotion types: FLATOFF | PERCENTOFF | FREEDELIVERY | BOGO | FREEITEM_MINBASKET | MENU_ITEM_DISCOUNT."
    ),
)
def get_promotion(
    promotion_id: Annotated[str, Path(description="The Uber Eats promotion UUID.")],
    client: Annotated[UberEatsClient, Depends(get_client)],
) -> BasePromotion:
    return client.promotions.get(promotion_id=promotion_id)


@router.get(
    "/stores/{store_id}/promotions",
    response_model=PromotionList,
    summary="List promotions for a store",
    description=(
        "Retrieve all active promotions for a specific store. "
        "Each promotion in the list is typed according to its promo_type. "
        "Use this endpoint to audit active discounts before creating new ones."
    ),
)
def list_promotions(
    store_id: Annotated[str, Path(description="The Uber Eats store UUID.")],
    client: Annotated[UberEatsClient, Depends(get_client)],
) -> PromotionList:
    return client.promotions.list(store_id=store_id)
