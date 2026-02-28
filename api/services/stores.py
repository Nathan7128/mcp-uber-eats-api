from __future__ import annotations
from typing import TYPE_CHECKING

from api.models.stores import Store, StoreList, StoreStatusResponse

if TYPE_CHECKING:
    from api.client import UberEatsClient


class StoresService:
    """Wrapper for the Uber Eats Marketplace Store API.

    Endpoints covered:
    - GET  /v1/delivery/stores                                      → list()
    - GET  /v1/delivery/store/{store_id}                            → get()
    - POST /v1/delivery/store/{store_id}                            → update()
    - GET  /v1/delivery/store/{store_id}/status                     → get_status()
    - POST /v1/delivery/store/{store_id}/update-store-status        → update_status()
    - POST /v1/delivery/store/{store_id}/update-store-prep-time     → update_prep_time()
    - POST /v1/delivery/store/{store_id}/update-fulfillment-configuration → update_fulfillment_config()
    """

    def __init__(self, client: UberEatsClient):
        self._client = client

    # ------------------------------------------------------------------
    # GET /v1/delivery/stores
    # ------------------------------------------------------------------

    def list(self, next_page_token: str = None, limit: int = None) -> StoreList:
        """List all stores associated with the authenticated account.

        Args:
            next_page_token: Token for pagination (from a previous response).
            limit: Maximum number of stores to return per page.

        Returns:
            StoreList with .data (list of Store) and .pagination_data.
        """
        params = {}
        if next_page_token is not None:
            params["next_page_token"] = next_page_token
        if limit is not None:
            params["limit"] = limit
        data = self._client.get("/v1/delivery/stores", params=params or None)
        return StoreList.model_validate(data)

    # ------------------------------------------------------------------
    # GET /v1/delivery/store/{store_id}
    # ------------------------------------------------------------------

    def get(self, store_id: str, expand: list[str] = None) -> Store:
        """Retrieve details for a specific store.

        Args:
            store_id: The Uber Eats store UUID.
            expand: Optional list of fields to expand (e.g. ["hours", "special_hours"]).

        Returns:
            Store object.
        """
        params = {}
        if expand:
            params["expand"] = ",".join(expand)
        data = self._client.get(f"/v1/delivery/store/{store_id}", params=params or None)
        return Store.model_validate(data)

    # ------------------------------------------------------------------
    # POST /v1/delivery/store/{store_id}
    # ------------------------------------------------------------------

    def update(self, store_id: str, contact: dict = None, location: dict = None,
               pickup_instructions: str = None) -> Store:
        """Update store information.

        Args:
            store_id: The Uber Eats store UUID.
            contact: Contact info dict (e.g. {"phone": "...", "first_name": "...", "last_name": "..."}).
            location: Location info dict.
            pickup_instructions: Text instructions for couriers picking up orders.

        Returns:
            Updated Store object.
        """
        body = {}
        if contact is not None:
            body["contact"] = contact
        if location is not None:
            body["location"] = location
        if pickup_instructions is not None:
            body["pickup_instructions"] = pickup_instructions
        data = self._client.post(f"/v1/delivery/store/{store_id}", json=body)
        return Store.model_validate(data)

    # ------------------------------------------------------------------
    # GET /v1/delivery/store/{store_id}/status
    # ------------------------------------------------------------------

    def get_status(self, store_id: str) -> StoreStatusResponse:
        """Retrieve the current online/offline status of a store.

        Args:
            store_id: The Uber Eats store UUID.

        Returns:
            StoreStatusResponse with .status, .reason, .is_offline_until.
            Use .is_online for a quick boolean check.
        """
        data = self._client.get(f"/v1/delivery/store/{store_id}/status")
        return StoreStatusResponse.model_validate(data)

    # ------------------------------------------------------------------
    # POST /v1/delivery/store/{store_id}/update-store-status
    # ------------------------------------------------------------------

    def update_status(self, store_id: str, status: str, reason: str = None,
                      is_offline_until: str = None) -> Store:
        """Set the store online or offline.

        Args:
            store_id: The Uber Eats store UUID.
            status: "ONLINE" or "OFFLINE".
            reason: Reason for the status change (required when going OFFLINE).
            is_offline_until: RFC3339 timestamp indicating when the store will come back online.

        Returns:
            Updated Store object.
        """
        body = {"status": status}
        if reason is not None:
            body["reason"] = reason
        if is_offline_until is not None:
            body["is_offline_until"] = is_offline_until
        data = self._client.post(f"/v1/delivery/store/{store_id}/update-store-status", json=body)
        return Store.model_validate(data)

    # ------------------------------------------------------------------
    # POST /v1/delivery/store/{store_id}/update-store-prep-time
    # ------------------------------------------------------------------

    def update_prep_time(self, store_id: str, original_prep_time: int,
                         updated_prep_time: int) -> dict:
        """Update the food preparation time for a store.

        Args:
            store_id: The Uber Eats store UUID.
            original_prep_time: Current prep time in minutes.
            updated_prep_time: New prep time in minutes.

        Returns:
            Success response.
        """
        body = {
            "original_prep_time": original_prep_time,
            "updated_prep_time": updated_prep_time,
        }
        return self._client.post(f"/v1/delivery/store/{store_id}/update-store-prep-time", json=body)

    # ------------------------------------------------------------------
    # POST /v1/delivery/store/{store_id}/update-fulfillment-configuration
    # ------------------------------------------------------------------

    def update_fulfillment_config(self, store_id: str, override_config: dict) -> dict:
        """Update the fulfillment configuration for a store.

        Args:
            store_id: The Uber Eats store UUID.
            override_config: Config overrides, e.g.:
                {"custom_min_etd_minutes": 30}  (max 160 minutes)

        Returns:
            Success response.
        """
        body = {"override_config": override_config}
        return self._client.post(
            f"/v1/delivery/store/{store_id}/update-fulfillment-configuration", json=body
        )
