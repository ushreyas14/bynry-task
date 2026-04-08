import uuid
from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, UniqueConstraint

from app.extensions import db


def utcnow():
    return datetime.now(timezone.utc)


class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    plan = db.Column(db.String(50), nullable=False, default="starter")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)


class Warehouse(db.Model):
    __tablename__ = "warehouses"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = db.Column(
        db.String(36), db.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)


class Product(db.Model):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("company_id", "sku", name="uq_products_company_sku"),
    )

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = db.Column(
        db.String(36), db.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    name = db.Column(db.String(255), nullable=False)
    sku = db.Column(db.String(100), nullable=False)
    product_type = db.Column(db.String(50), nullable=False, default="standard")
    price = db.Column(db.Numeric(12, 4), nullable=False)
    low_stock_threshold = db.Column(db.Integer, nullable=False, default=10)
    description = db.Column(db.Text, nullable=True)
    is_bundle = db.Column(db.Boolean, nullable=False, default=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)


class Inventory(db.Model):
    __tablename__ = "inventory"
    __table_args__ = (
        UniqueConstraint("product_id", "warehouse_id", name="uq_inventory_product_warehouse"),
        CheckConstraint("quantity >= 0", name="ck_inventory_quantity_non_negative"),
    )

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = db.Column(
        db.String(36), db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    warehouse_id = db.Column(
        db.String(36), db.ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False
    )
    quantity = db.Column(db.Integer, nullable=False, default=0)
    updated_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow
    )


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)


class InventoryChange(db.Model):
    __tablename__ = "inventory_changes"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    inventory_id = db.Column(
        db.String(36), db.ForeignKey("inventory.id", ondelete="CASCADE"), nullable=False
    )
    changed_by = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="SET NULL"))
    delta = db.Column(db.Integer, nullable=False)
    quantity_after = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)


class Supplier(db.Model):
    __tablename__ = "suppliers"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = db.Column(
        db.String(36), db.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    name = db.Column(db.String(255), nullable=False)
    contact_email = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)


class ProductSupplier(db.Model):
    __tablename__ = "product_suppliers"
    __table_args__ = (
        UniqueConstraint("product_id", "supplier_id", name="uq_product_supplier"),
    )

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = db.Column(
        db.String(36), db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    supplier_id = db.Column(
        db.String(36), db.ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False
    )
    unit_cost = db.Column(db.Numeric(12, 4), nullable=True)
    lead_time_days = db.Column(db.Integer, nullable=True)
    is_preferred = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)


class BundleItem(db.Model):
    __tablename__ = "bundle_items"
    __table_args__ = (
        UniqueConstraint(
            "bundle_product_id", "component_product_id", name="uq_bundle_component"
        ),
        CheckConstraint("quantity > 0", name="ck_bundle_item_quantity_positive"),
    )

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bundle_product_id = db.Column(
        db.String(36), db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    component_product_id = db.Column(
        db.String(36), db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    quantity = db.Column(db.Integer, nullable=False)
