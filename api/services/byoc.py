from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from api.client import UberEatsClient


class BYOCService:
    """Wrapper for the Uber Eats Delivery BYOC API (Bring Your Own Courier).

    Allows merchants using their own couriers to push live location data
    to the Uber Eats platform so customers can track their delivery.

    Endpoints covered:
    - POST /v1/eats/byoc/restaurants/orders/event/location → ingest_courier_location()
    """

    def __init__(self, client: UberEatsClient):
        self._client = client

    # ------------------------------------------------------------------
    # POST /v1/eats/byoc/restaurants/orders/event/location
    # ------------------------------------------------------------------

    def ingest_courier_location(
        self,
        order_workflow_uuid: str,
        restaurant_uuid: str,
        location_events: list[dict],
        is_batched_order: bool = False,
    ) -> dict:
        """Push courier live location events to Uber Eats for customer tracking.

        Args:
            order_workflow_uuid: UUID of the order workflow (order ID).
            restaurant_uuid: UUID of the restaurant/store.
            location_events: List of location event dicts. Each event must contain:
                {
                    "position_event": {
                        "point": {"latitude": float, "longitude": float},
                        "time": {"epochMillis": int}
                    },
                    "eta_in_minutes": int  # optional
                }
            is_batched_order: Whether this is a batched order. Defaults to False.

        Returns:
            {"message": "success"}

        Example:
            byoc.ingest_courier_location(
                order_workflow_uuid="550e8400-e29b-41d4-a716-446655440000",
                restaurant_uuid="6ba7b810-9dad-11d1-80b4-00c04fd430c8",
                location_events=[{
                    "position_event": {
                        "point": {"latitude": 48.8566, "longitude": 2.3522},
                        "time": {"epochMillis": 1700000000000}
                    },
                    "eta_in_minutes": 12
                }]
            )
        """
        body = {
            "order_workflow_uuid": order_workflow_uuid,
            "restaurant_uuid": restaurant_uuid,
            "is_batched_order": is_batched_order,
            "location_events": location_events,
        }
        return self._client.post("/v1/eats/byoc/restaurants/orders/event/location", json=body)
