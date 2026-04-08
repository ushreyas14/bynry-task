from datetime import datetime, timedelta, timezone

from flask import Blueprint, abort, current_app, jsonify
from sqlalchemy import text

from app.extensions import db
from app.models import Company


alerts_bp = Blueprint("alerts", __name__)


@alerts_bp.get("/api/companies/<string:company_id>/alerts/low-stock")
def low_stock_alerts(company_id):
    company = Company.query.filter_by(id=company_id).first()
    if not company:
        abort(404, description="Company not found")

    sales_window_days = current_app.config["SALES_WINDOW_DAYS"]
    cutoff = datetime.now(timezone.utc) - timedelta(days=sales_window_days)

    # This query is optimized for PostgreSQL and avoids N+1 supplier lookups.
    query = text(
        """
        WITH recent_sales AS (
            SELECT
                ic.inventory_id,
                ABS(SUM(ic.delta))::float / :window_days AS avg_daily_sales
            FROM inventory_changes ic
            WHERE ic.created_at >= :cutoff
              AND ic.delta < 0
              AND ic.reason = 'sale'
            GROUP BY ic.inventory_id
        )
        SELECT
            p.id AS product_id,
            p.name AS product_name,
            p.sku,
            p.low_stock_threshold AS threshold,
            w.id AS warehouse_id,
            w.name AS warehouse_name,
            i.quantity AS current_stock,
            rs.avg_daily_sales,
            sup.supplier_id,
            sup.supplier_name,
            sup.contact_email
        FROM inventory i
        JOIN products p
          ON p.id = i.product_id
         AND p.company_id = :company_id
         AND p.is_active = true
        JOIN warehouses w
          ON w.id = i.warehouse_id
         AND w.company_id = :company_id
         AND w.is_active = true
        JOIN recent_sales rs
          ON rs.inventory_id = i.id
        LEFT JOIN LATERAL (
            SELECT
                ps.supplier_id,
                s2.name AS supplier_name,
                s2.contact_email
            FROM product_suppliers ps
            JOIN suppliers s2
              ON s2.id = ps.supplier_id
            WHERE ps.product_id = p.id
            ORDER BY ps.is_preferred DESC, ps.created_at ASC
            LIMIT 1
        ) sup ON true
        WHERE i.quantity < p.low_stock_threshold
        ORDER BY (i.quantity::float / NULLIF(p.low_stock_threshold, 0)) ASC
        """
    )

    rows = db.session.execute(
        query,
        {
            "company_id": company_id,
            "cutoff": cutoff,
            "window_days": sales_window_days,
        },
    ).fetchall()

    alerts = []
    for row in rows:
        avg_daily_sales = row.avg_daily_sales or 0
        days_until_stockout = (
            round(row.current_stock / avg_daily_sales) if avg_daily_sales > 0 else None
        )
        alerts.append(
            {
                "product_id": row.product_id,
                "product_name": row.product_name,
                "sku": row.sku,
                "warehouse_id": row.warehouse_id,
                "warehouse_name": row.warehouse_name,
                "current_stock": row.current_stock,
                "threshold": row.threshold,
                "days_until_stockout": days_until_stockout,
                "supplier": (
                    {
                        "id": row.supplier_id,
                        "name": row.supplier_name,
                        "contact_email": row.contact_email,
                    }
                    if row.supplier_id
                    else None
                ),
            }
        )

    return jsonify({"alerts": alerts, "total_alerts": len(alerts)}), 200
