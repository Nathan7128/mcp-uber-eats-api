from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Path, Query

from app.client import UberEatsClient
from app.models.orders import OrderList, RestaurantOrder
from app.dependencies import get_client

router = APIRouter(tags=["Orders"])


@router.get(
    "/orders/{order_id}",
    response_model=RestaurantOrder,
    summary="Get an order by ID",
    description=(
        "Retrieve full details for a specific order by its UUID. "
        "The response contains the order wrapper (RestaurantOrder) with the inner Order accessible via .order. "
        "Use expand to include related data such as cart items, delivery tracking, or payment information."
    ),
)
def get_order(
    order_id: Annotated[str, Path(description="The Uber Eats order UUID.")],
    client: Annotated[UberEatsClient, Depends(get_client)],
    expand: Annotated[
        Optional[List[str]],
        Query(description="Fields to expand. Possible values: carts, deliveries, payment."),
    ] = None,
) -> RestaurantOrder:
    return client.orders.get(order_id=order_id, expand=expand)


@router.get(
    "/stores/{store_id}/orders",
    response_model=OrderList,
    summary="List orders for a store",
    description=(
        "Retrieve the list of orders for a specific store. Orders are limited to the last 60 days. "
        "Filter by state (lifecycle stage of the order) or status (scheduling status). "
        "Use start_time and end_time (RFC3339) to narrow the time range. "
        "Paginate using next_page_token from the previous response. "
        "Use .orders on the response for a flat list of Order objects."
    ),
)
def list_orders(
    store_id: Annotated[str, Path(description="The Uber Eats store UUID.")],
    client: Annotated[UberEatsClient, Depends(get_client)],
    expand: Annotated[
        Optional[List[str]],
        Query(description="Fields to expand. Possible values: carts, deliveries, payment."),
    ] = None,
    state: Annotated[
        Optional[str],
        Query(description="Filter by order state. Possible values: OFFERED | ACCEPTED | HANDED_OFF | SUCCEEDED | FAILED | UNKNOWN."),
    ] = None,
    status: Annotated[
        Optional[str],
        Query(description="Filter by order scheduling status. Possible values: SCHEDULED | ACTIVE | COMPLETED | UNKNOWN."),
    ] = None,
    start_time: Annotated[
        Optional[str],
        Query(description="Start of the time range in RFC3339 format (e.g. 2024-01-01T00:00:00Z). Orders are limited to the last 60 days."),
    ] = None,
    end_time: Annotated[
        Optional[str],
        Query(description="End of the time range in RFC3339 format (e.g. 2024-01-31T23:59:59Z)."),
    ] = None,
    next_page_token: Annotated[
        Optional[str],
        Query(description="Pagination token returned by a previous call. Pass it to retrieve the next page."),
    ] = None,
    page_size: Annotated[
        Optional[int],
        Query(description="Number of orders per page. Between 1 and 50. Defaults to 50.", ge=1, le=50),
    ] = None,
) -> OrderList:
    return client.orders.list(
        store_id=store_id,
        expand=expand,
        state=state,
        status=status,
        start_time=start_time,
        end_time=end_time,
        next_page_token=next_page_token,
        page_size=page_size,
    )
