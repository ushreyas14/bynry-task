from flask import Blueprint, current_app, jsonify, request
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Company, Inventory, InventoryChange, Product, Warehouse
from app.services.validation import validate_create_product_payload


products_bp = Blueprint("products", __name__)


@products_bp.post("/api/products")
def create_product():
    payload = request.get_json(silent=True)
    data, error = validate_create_product_payload(payload)
    if error:
        message, code = error
        return jsonify({"error": message}), code

    company = Company.query.filter_by(id=data["company_id"]).first()
    if not company:
        return jsonify({"error": "company_id does not exist"}), 422

    warehouse = Warehouse.query.filter_by(
        id=data["warehouse_id"], company_id=data["company_id"], is_active=True
    ).first()
    if not warehouse:
        return jsonify({"error": "warehouse_id is invalid for this company"}), 422

    actor_id = request.headers.get("X-User-Id")

    try:
        product = Product(
            company_id=data["company_id"],
            name=data["name"],
            sku=data["sku"],
            price=data["price"],
            description=data["description"],
            product_type=data["product_type"],
            low_stock_threshold=data["low_stock_threshold"],
            is_bundle=data["is_bundle"],
        )
        db.session.add(product)
        db.session.flush()

        inventory = Inventory(
            product_id=product.id,
            warehouse_id=data["warehouse_id"],
            quantity=data["initial_quantity"],
        )
        db.session.add(inventory)
        db.session.flush()

        db.session.add(
            InventoryChange(
                inventory_id=inventory.id,
                changed_by=actor_id,
                delta=data["initial_quantity"],
                quantity_after=data["initial_quantity"],
                reason="receipt",
            )
        )

        db.session.commit()

    except IntegrityError as exc:
        db.session.rollback()
        if "sku" in str(exc.orig).lower():
            return jsonify({"error": "SKU already exists for this company"}), 409
        return jsonify({"error": "Database constraint violation"}), 409
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Unexpected error creating product")
        return jsonify({"error": "Internal server error"}), 500

    return (
        jsonify(
            {
                "product": {
                    "id": product.id,
                    "company_id": product.company_id,
                    "name": product.name,
                    "sku": product.sku,
                    "price": str(product.price),
                    "warehouse_id": inventory.warehouse_id,
                    "initial_quantity": inventory.quantity,
                }
            }
        ),
        201,
    )
