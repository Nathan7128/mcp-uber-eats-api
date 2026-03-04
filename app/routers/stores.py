from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Path, Query

from app.client import UberEatsClient
from app.models.stores import Store, StoreList, StoreStatusResponse
from app.dependencies import get_client

router = APIRouter(tags=["Stores"])


@router.get(
    "/stores",
    response_model=StoreList,
    summary="List all stores",
    description=(
        "Retrieve the list of all Uber Eats stores associated with the authenticated account. "
        "Supports pagination via next_page_token. Use this endpoint to discover available store IDs "
        "before querying individual store details or orders."
    ),
)
def list_stores(
    client: Annotated[UberEatsClient, Depends(get_client)],
    next_page_token: Annotated[
        Optional[str],
        Query(description="Pagination token returned by a previous call to this endpoint. Pass it to retrieve the next page of results."),
    ] = None,
    limit: Annotated[
        Optional[int],
        Query(description="Maximum number of stores to return per page.", ge=1),
    ] = None,
) -> StoreList:
    return client.stores.list(next_page_token=next_page_token, limit=limit)


@router.get(
    "/stores/{store_id}",
    response_model=Store,
    summary="Get a store by ID",
    description=(
        "Retrieve detailed information about a specific Uber Eats store by its UUID. "
        "Use the expand parameter to include additional data such as opening hours or special hours."
    ),
)
def get_store(
    store_id: Annotated[str, Path(description="The Uber Eats store UUID.")],
    client: Annotated[UberEatsClient, Depends(get_client)],
    expand: Annotated[
        Optional[List[str]],
        Query(description="Comma-separated list of fields to expand. Possible values: hours, special_hours, contact, location."),
    ] = None,
) -> Store:
    return client.stores.get(store_id=store_id, expand=expand)


@router.get(
    "/stores/{store_id}/status",
    response_model=StoreStatusResponse,
    summary="Get store online/offline status",
    description=(
        "Check whether a specific store is currently online or offline. "
        "The response includes the current status, the reason for any offline state, "
        "and the timestamp until which the store will remain offline (if applicable). "
        "Use the is_online convenience property for a quick boolean check."
    ),
)
def get_store_status(
    store_id: Annotated[str, Path(description="The Uber Eats store UUID.")],
    client: Annotated[UberEatsClient, Depends(get_client)],
) -> StoreStatusResponse:
    return client.stores.get_status(store_id=store_id)
