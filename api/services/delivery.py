from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from api.client import UberEatsClient


class DeliveryService:
    """Wrapper for the Uber Eats Delivery Partner API.

    Supports the Dispatch Multiple Couriers (DMC) feature, which allows
    sending multiple couriers to pick up a single large order.

    Endpoints covered:
    - POST /v1/delivery/order/{order_id}/update-delivery-partner-count → update_partner_count()

    DMC availability:
        Americas: NYC Manhattan, Costa Rica, Dominican Republic, Ecuador,
                  El Salvador, Guatemala, Panama
        Europe/Middle East: France, Germany, Netherlands, Spain, Italy,
                            Portugal, Ukraine, Sweden, Ireland, UK (select),
                            Switzerland (select), Poland (select), Norway (select),
                            UAE (select)
        Africa: South Africa, Kenya
        Asia: Japan, Hong Kong, Taiwan, Sri Lanka (Colombo)
    """

    def __init__(self, client: UberEatsClient):
        self._client = client

    # ------------------------------------------------------------------
    # POST /v1/delivery/order/{order_id}/update-delivery-partner-count
    # ------------------------------------------------------------------

    def update_partner_count(self, order_id: str, delivery_partner_count: int) -> dict:
        """Set the number of couriers to dispatch for a large order (DMC feature).

        Couriers can be added or reduced up to 10 minutes after the first courier
        starts. The merchant is responsible for dividing the order among couriers.

        Args:
            order_id: The Uber Eats order UUID.
            delivery_partner_count: Number of couriers (2–4; up to 5 in exceptional cases).

        Returns:
            Success response.
        """
        body = {"delivery_partner_count": delivery_partner_count}
        return self._client.post(
            f"/v1/delivery/order/{order_id}/update-delivery-partner-count", json=body
        )
