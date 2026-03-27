"""MCP Tools for the Uber Eats API — read-only operations for restaurateurs."""
import os
from typing import Any

from fastmcp import FastMCP

from mcp_server.client import UberEatsClient
from mcp_server.models.stores import StoreModel, StoreStatusModel, StoreListModel
from mcp_server.models.orders import OrderModel, OrderListModel
from mcp_server.models.promotions import PromotionModel, PromotionListModel

if os.getenv("MOCK_API", "").lower() in {"1", "true", "yes"}:
    from mcp_server.mock_client import MockUberEatsClient
    client = MockUberEatsClient()
else:
    client = UberEatsClient()

mcp = FastMCP(name="UberEatsAPIWrapper")


@mcp.tool(description="Liste tous les restaurants associés au compte Uber Eats.")
def list_stores(
    next_page_token: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """List all stores associated with the Uber Eats account."""
    params = {}
    if next_page_token:
        params["next_page_token"] = next_page_token
    if limit:
        params["limit"] = limit
    data = client.get("/v1/delivery/stores", params=params or None)
    return StoreListModel.model_validate(data).model_dump(exclude_none=True)


@mcp.tool(
    description=(
        "Récupère les informations d'un restaurant (horaires, adresse, configuration). "
        "Le paramètre expand accepte les valeurs : MENU, HOURS."
    )
)
def get_store(
    store_id: str,
    expand: list[str] | None = None,
) -> dict[str, Any]:
    """Get details for a single store (hours, address, configuration)."""
    params = {}
    if expand:
        params["expand"] = ",".join(expand)
    data = client.get(f"/v1/delivery/store/{store_id}", params=params or None)
    return StoreModel.model_validate(data).model_dump(exclude_none=True)


@mcp.tool(
    description="Vérifie si un restaurant est en ligne ou hors ligne, et la raison si hors ligne."
)
def get_store_status(store_id: str) -> dict[str, Any]:
    """Check whether a store is currently online or offline."""
    data = client.get(f"/v1/delivery/store/{store_id}/status")
    return StoreStatusModel.model_validate(data).model_dump(exclude_none=True)


@mcp.tool(
    description="Récupère tous les détails d'une commande (articles, prix, client, statut)."
)
def get_order(
    order_id: str,
    expand: list[str] | None = None,
) -> dict[str, Any]:
    """Get full details of a single order (items, customer, delivery status)."""
    params = {}
    if expand:
        params["expand"] = ",".join(expand)
    data = client.get(f"/v1/delivery/order/{order_id}", params=params or None)
    order_data = data.get("order", data)
    return OrderModel.model_validate(order_data).model_dump(exclude_none=True)


@mcp.tool(
    description=(
        "Liste les commandes d'un restaurant. Filtrable par statut ou période (max 60 jours). "
        "Valeurs possibles pour state : CREATED, OFFERED, ACCEPTED, HANDED_OFF, SUCCEEDED, FAILED. "
        "Valeurs possibles pour status : SCHEDULED, ACTIVE, COMPLETED."
    )
)
def list_store_orders(
    store_id: str,
    state: str | None = None,
    status: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    page_size: int | None = None,
    next_page_token: str | None = None,
) -> dict[str, Any]:
    """List orders for a store, with optional filters on state, status, and time range."""
    params = {}
    if state:
        params["state"] = state
    if status:
        params["status"] = status
    if start_time:
        params["start_time"] = start_time
    if end_time:
        params["end_time"] = end_time
    if page_size:
        params["page_size"] = page_size
    if next_page_token:
        params["next_page_token"] = next_page_token
    data = client.get(f"/v1/delivery/store/{store_id}/orders", params=params or None)
    return OrderListModel.model_validate(data).model_dump(exclude_none=True)


@mcp.tool(description="Récupère les détails d'une promotion spécifique.")
def get_promotion(promotion_id: str) -> dict[str, Any]:
    """Get details of a specific promotion."""
    data = client.get(f"/v1/delivery/promotions/{promotion_id}")
    return PromotionModel.model_validate(data).model_dump(exclude_none=True)


@mcp.tool(description="Liste toutes les promotions actives d'un restaurant.")
def list_store_promotions(store_id: str) -> dict[str, Any]:
    """List all active promotions for a store."""
    data = client.get(f"/v1/delivery/stores/{store_id}/promotions")
    return PromotionListModel.model_validate(data).model_dump(exclude_none=True)
