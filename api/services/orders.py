from __future__ import annotations
from typing import TYPE_CHECKING

from api.models.orders import RestaurantOrder, OrderList, AdjustPriceResponse

if TYPE_CHECKING:
    from api.client import UberEatsClient


class OrdersService:
    """Wrapper for the Uber Eats Order Fulfillment API.

    Endpoints covered:
    - GET  /v1/delivery/order/{order_id}                                → get()
    - GET  /v1/delivery/store/{store_id}/orders                         → list()
    - POST /v1/delivery/order/{order_id}/accept                         → accept()
    - POST /v1/delivery/order/{order_id}/deny                           → deny()
    - POST /v1/delivery/order/{order_id}/cancel                         → cancel()
    - POST /v1/delivery/order/{order_id}/ready                          → mark_ready()
    - POST /v1/delivery/order/{order_id}/adjust-price                   → adjust_price()
    - POST /v1/delivery/order/{order_id}/update-ready-time              → update_ready_time()
    - POST /v1/delivery/order/{order_id}/resolve-fulfillment-issues     → resolve_fulfillment_issues()
    - POST /v1/delivery/order/get-replacement-recommendations           → get_replacement_recommendations()
    """

    def __init__(self, client: UberEatsClient):
        self._client = client

    # ------------------------------------------------------------------
    # GET /v1/delivery/order/{order_id}
    # ------------------------------------------------------------------

    def get(self, order_id: str, expand: list[str] = None) -> RestaurantOrder:
        """Retrieve details for a specific order.

        Args:
            order_id: The Uber Eats order UUID.
            expand: Optional fields to expand. Possible values: ["carts", "deliveries", "payment"].

        Returns:
            RestaurantOrder — access the inner order via .order.
        """
        params = {}
        if expand:
            params["expand"] = ",".join(expand)
        data = self._client.get(f"/v1/delivery/order/{order_id}", params=params or None)
        return RestaurantOrder.model_validate(data)

    # ------------------------------------------------------------------
    # GET /v1/delivery/store/{store_id}/orders
    # ------------------------------------------------------------------

    def list(
        self,
        store_id: str,
        expand: list[str] = None,
        state: str = None,
        status: str = None,
        start_time: str = None,
        end_time: str = None,
        next_page_token: str = None,
        page_size: int = None,
    ) -> OrderList:
        """List orders for a store.

        Orders are limited to the last 60 days.

        Args:
            store_id: The Uber Eats store UUID.
            expand: Fields to expand (e.g. ["carts", "deliveries", "payment"]).
            state: Filter by order state. One of:
                "OFFERED", "ACCEPTED", "HANDED_OFF", "SUCCEEDED", "FAILED", "UNKNOWN".
            status: Filter by order status. One of:
                "SCHEDULED", "ACTIVE", "COMPLETED", "UNKNOWN".
            start_time: RFC3339 timestamp for the start of the time range.
            end_time: RFC3339 timestamp for the end of the time range.
            next_page_token: Pagination token from a previous response.
            page_size: Number of results per page (1–50, default 50).

        Returns:
            OrderList — use .orders for a flat list of Order objects,
            or .data for the raw list of RestaurantOrder wrappers.
        """
        params = {}
        if expand:
            params["expand"] = ",".join(expand)
        if state is not None:
            params["state"] = state
        if status is not None:
            params["status"] = status
        if start_time is not None:
            params["start_time"] = start_time
        if end_time is not None:
            params["end_time"] = end_time
        if next_page_token is not None:
            params["next_page_token"] = next_page_token
        if page_size is not None:
            params["page_size"] = page_size
        data = self._client.get(f"/v1/delivery/store/{store_id}/orders", params=params or None)
        return OrderList.model_validate(data)

    # ------------------------------------------------------------------
    # POST /v1/delivery/order/{order_id}/accept
    # ------------------------------------------------------------------

    def accept(
        self,
        order_id: str,
        ready_for_pickup_time: str = None,
        external_reference_id: str = None,
        accepted_by: str = None,
        order_pickup_instructions: str = None,
    ) -> dict:
        """Accept an incoming order.

        Args:
            order_id: The Uber Eats order UUID.
            ready_for_pickup_time: RFC3339 timestamp when the order will be ready.
            external_reference_id: Your internal order reference ID.
            accepted_by: Name or ID of the person accepting the order.
            order_pickup_instructions: Instructions for the courier at pickup.

        Returns:
            Success response.
        """
        body = {}
        if ready_for_pickup_time is not None:
            body["ready_for_pickup_time"] = ready_for_pickup_time
        if external_reference_id is not None:
            body["external_reference_id"] = external_reference_id
        if accepted_by is not None:
            body["accepted_by"] = accepted_by
        if order_pickup_instructions is not None:
            body["order_pickup_instructions"] = order_pickup_instructions
        return self._client.post(f"/v1/delivery/order/{order_id}/accept", json=body)

    # ------------------------------------------------------------------
    # POST /v1/delivery/order/{order_id}/deny
    # ------------------------------------------------------------------

    def deny(self, order_id: str, reason: str) -> dict:
        """Deny an incoming order.

        Args:
            order_id: The Uber Eats order UUID.
            reason: Denial reason code. Common values:
                "STORE_CLOSED", "ITEM_UNAVAILABLE", "CANNOT_COMPLETE_CUSTOMER_NOTE",
                "REASON_UNKNOWN", "TOO_BUSY".

        Returns:
            Success response.
        """
        body = {"reason": reason}
        return self._client.post(f"/v1/delivery/order/{order_id}/deny", json=body)

    # ------------------------------------------------------------------
    # POST /v1/delivery/order/{order_id}/cancel
    # ------------------------------------------------------------------

    def cancel(self, order_id: str, reason: str) -> dict:
        """Cancel an accepted order.

        Args:
            order_id: The Uber Eats order UUID.
            reason: Cancellation reason code. Common values:
                "OUT_OF_ITEMS", "KITCHEN_CLOSED", "CUSTOMER_CALLED_TO_CANCEL",
                "RESTAURANT_TOO_BUSY", "CANNOT_COMPLETE_CUSTOMER_NOTE",
                "ORDER_PLACED_IN_ERROR".

        Returns:
            Empty dict (204 No Content on success).
        """
        body = {"reason": reason}
        return self._client.post(f"/v1/delivery/order/{order_id}/cancel", json=body)

    # ------------------------------------------------------------------
    # POST /v1/delivery/order/{order_id}/ready
    # ------------------------------------------------------------------

    def mark_ready(self, order_id: str) -> dict:
        """Mark an order as ready for pickup.

        Args:
            order_id: The Uber Eats order UUID.

        Returns:
            Success response.
        """
        return self._client.post(f"/v1/delivery/order/{order_id}/ready", json={})

    # ------------------------------------------------------------------
    # POST /v1/delivery/order/{order_id}/adjust-price
    # ------------------------------------------------------------------

    def adjust_price(self, order_id: str, items: list[dict]) -> AdjustPriceResponse:
        """Adjust the price of items in an order (e.g. for out-of-stock substitutions).

        Args:
            order_id: The Uber Eats order UUID.
            items: List of item price adjustments, e.g.:
                [{"item_id": "...", "price": {"amount": 599, "currency_code": "USD"}}]

        Returns:
            {"tax_rate_applied": bool}
        """
        body = {"items": items}
        data = self._client.post(f"/v1/delivery/order/{order_id}/adjust-price", json=body)
        return AdjustPriceResponse.model_validate(data)

    # ------------------------------------------------------------------
    # POST /v1/delivery/order/{order_id}/update-ready-time
    # ------------------------------------------------------------------

    def update_ready_time(self, order_id: str, ready_for_pickup_time: str) -> dict:
        """Update the estimated ready-for-pickup time for an order.

        Args:
            order_id: The Uber Eats order UUID.
            ready_for_pickup_time: RFC3339 timestamp for the new ready time.

        Returns:
            Success response.
        """
        body = {"ready_for_pickup_time": ready_for_pickup_time}
        return self._client.post(f"/v1/delivery/order/{order_id}/update-ready-time", json=body)

    # ------------------------------------------------------------------
    # POST /v1/delivery/order/{order_id}/resolve-fulfillment-issues
    # ------------------------------------------------------------------

    def resolve_fulfillment_issues(self, order_id: str, resolution: dict) -> dict:
        """Report how fulfillment issues (e.g. out-of-stock items) were resolved.

        For restaurant orders:
            resolution = {
                "items_unavailable": [{"item_id": "...", "quantity": 1, ...}]
            }

        For retail orders:
            resolution = {
                "line_items": [{
                    "instance_id": "...",
                    "resolution": "SUBSTITUTED" | "REMOVED",
                    "substituted_item": {...}  # only for SUBSTITUTED
                }]
            }

        Args:
            order_id: The Uber Eats order UUID.
            resolution: Resolution payload (restaurant or retail format).

        Returns:
            Resolution confirmation response.
        """
        return self._client.post(
            f"/v1/delivery/order/{order_id}/resolve-fulfillment-issues", json=resolution
        )

    # ------------------------------------------------------------------
    # POST /v1/delivery/order/get-replacement-recommendations
    # ------------------------------------------------------------------

    def get_replacement_recommendations(self, items: list[dict], store_id: str = None) -> dict:
        """Get recommended replacement items for out-of-stock products (retail only).

        Args:
            items: List of out-of-stock items to find replacements for, e.g.:
                [{"item_id": "...", "quantity": 1}]
            store_id: The store UUID (required for replacement lookup).

        Returns:
            {"recommendations": [{...}, ...]}
        """
        body = {"items": items}
        if store_id is not None:
            body["store_id"] = store_id
        return self._client.post("/v1/delivery/order/get-replacement-recommendations", json=body)
