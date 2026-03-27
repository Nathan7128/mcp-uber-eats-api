from pydantic import BaseModel, ConfigDict, model_validator

__all__ = ["OrderItemModel", "OrderModel", "OrderListModel"]


class ModifierModel(BaseModel):
    """A modifier group applied to an order item (e.g. 'Sauces': ['Ketchup', 'Mayo'])."""

    model_config = ConfigDict(extra="ignore")

    group: str | None = None
    options: list[str] | None = None


class OrderItemModel(BaseModel):
    """A single item in a customer order.

    Flattens nested API fields: title → name,
    quantity.amount → quantity,
    customer_request → special_instructions,
    selected_modifier_groups → modifiers.
    """

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str | None = None
    name: str | None = None
    quantity: float | None = None
    special_instructions: str | None = None
    modifiers: list[ModifierModel] | None = None

    @model_validator(mode="before")
    @classmethod
    def extract_fields(cls, values: dict) -> dict:
        # name from title
        if "title" in values and "name" not in values:
            values["name"] = values["title"]

        # quantity from nested quantity.amount
        qty_obj = values.get("quantity") or {}
        if isinstance(qty_obj, dict):
            values["quantity"] = qty_obj.get("amount")

        # special_instructions from customer_request
        cr = values.get("customer_request") or {}
        if isinstance(cr, dict):
            values["special_instructions"] = cr.get("special_instructions")

        # modifiers from selected_modifier_groups
        mods = []
        for mg in values.get("selected_modifier_groups") or []:
            if isinstance(mg, dict):
                opts = [
                    item.get("title")
                    for item in (mg.get("selected_items") or [])
                    if isinstance(item, dict) and item.get("title")
                ]
                mods.append({"group": mg.get("title"), "options": opts})
        if mods:
            values["modifiers"] = mods

        return values


class OrderModel(BaseModel):
    """Full order details including customer info, items, and delivery status.

    Flattens nested API fields: customers[] → customer_name/customer_phone,
    carts[].items[] → items, deliveries[0].status → delivery_status.
    """

    model_config = ConfigDict(extra="ignore")

    id: str | None = None
    display_id: str | None = None
    state: str | None = None
    status: str | None = None
    fulfillment_type: str | None = None
    customer_name: str | None = None
    customer_phone: str | None = None
    items: list[OrderItemModel] | None = None
    item_count: int | None = None
    created_time: str | None = None
    ready_for_pickup_time: str | None = None
    store_instructions: str | None = None
    delivery_status: str | None = None

    @model_validator(mode="before")
    @classmethod
    def extract_fields(cls, values: dict) -> dict:
        # Extract primary customer info
        customers = values.get("customers") or []
        if customers:
            primary = next(
                (c for c in customers if isinstance(c, dict) and c.get("is_primary_customer")),
                customers[0],
            )
            if isinstance(primary, dict):
                name_obj = primary.get("name") or {}
                if isinstance(name_obj, dict):
                    values["customer_name"] = (
                        name_obj.get("display_name")
                        or f"{name_obj.get('first_name', '')} {name_obj.get('last_name', '')}".strip()
                        or None
                    )
                contact_obj = primary.get("contact") or {}
                if isinstance(contact_obj, dict):
                    phone_obj = contact_obj.get("phone") or {}
                    if isinstance(phone_obj, dict):
                        values["customer_phone"] = phone_obj.get("number")

        # Extract items from all carts and compute item_count
        all_items = []
        total_count = 0
        for cart in values.get("carts") or []:
            if isinstance(cart, dict):
                for item in cart.get("items") or []:
                    if isinstance(item, dict):
                        all_items.append(item)
                        qty_obj = item.get("quantity") or {}
                        if isinstance(qty_obj, dict):
                            total_count += int(qty_obj.get("amount") or 0)
        if all_items:
            values["items"] = all_items
        values["item_count"] = total_count

        # Extract delivery status from first delivery
        deliveries = values.get("deliveries") or []
        if deliveries and isinstance(deliveries[0], dict):
            values["delivery_status"] = deliveries[0].get("status")

        return values


class OrderListModel(BaseModel):
    """Paginated list of orders for a store."""

    model_config = ConfigDict(extra="ignore")

    orders: list[OrderModel] | None = None
    total_count: int | None = None
    next_page_token: str | None = None

    @model_validator(mode="before")
    @classmethod
    def extract_fields(cls, values: dict) -> dict:
        # Unwrap RestaurantOrder wrappers: {"order": {...}}
        raw_data = values.get("data") or []
        orders = []
        for entry in raw_data:
            if isinstance(entry, dict):
                order = entry.get("order", entry)
                if order:
                    orders.append(order)
        if orders:
            values["orders"] = orders

        # Extract pagination
        pagination = values.get("pagination_data") or {}
        if isinstance(pagination, dict):
            values["next_page_token"] = pagination.get("next_page_token")
            values["total_count"] = pagination.get("total_count")

        return values
