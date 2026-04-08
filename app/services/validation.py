from decimal import Decimal, InvalidOperation


def validate_create_product_payload(payload):
    if not isinstance(payload, dict):
        return None, ("Request body must be JSON", 400)

    required = [
        "company_id",
        "name",
        "sku",
        "price",
        "warehouse_id",
        "initial_quantity",
    ]
    missing = [field for field in required if field not in payload]
    if missing:
        return None, (f"Missing fields: {', '.join(missing)}", 422)

    sku = str(payload["sku"]).strip().upper()
    name = str(payload["name"]).strip()
    company_id = str(payload["company_id"]).strip()
    warehouse_id = str(payload["warehouse_id"]).strip()

    if not sku or not name:
        return None, ("name and sku must be non-empty strings", 422)

    try:
        price = Decimal(str(payload["price"]))
        if price < 0:
            raise ValueError
    except (InvalidOperation, ValueError):
        return None, ("price must be a non-negative decimal", 422)

    quantity = payload["initial_quantity"]
    if not isinstance(quantity, int) or quantity < 0:
        return None, ("initial_quantity must be a non-negative integer", 422)

    threshold = payload.get("low_stock_threshold", 10)
    if not isinstance(threshold, int) or threshold < 0:
        return None, ("low_stock_threshold must be a non-negative integer", 422)

    cleaned = {
        "company_id": company_id,
        "warehouse_id": warehouse_id,
        "name": name,
        "sku": sku,
        "price": price,
        "initial_quantity": quantity,
        "description": payload.get("description"),
        "product_type": payload.get("product_type", "standard"),
        "low_stock_threshold": threshold,
        "is_bundle": bool(payload.get("is_bundle", False)),
    }
    return cleaned, None
