# StockFlow

Inventory Management System API for the take-home assessment, covering:

- Part 1: Product creation endpoint with transaction safety, validation, and clean error handling
- Part 2: Relational schema for multi-company, multi-warehouse inventory
- Part 3: Low-stock alerts endpoint using sales velocity and preferred supplier fallback

## Project Structure

```text
stockflow/
  app/
    __init__.py
    config.py
    extensions.py
    models.py
    routes/
      health.py
      products.py
      alerts.py
    services/
      validation.py
  db/
    schema.sql
  tests/
    conftest.py
    test_products_api.py
  .env.example
  .gitignore
  requirements.txt
  run.py
```

## Setup

1. Create and activate virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set environment variables from `.env.example`.
4. Create database schema (PostgreSQL):

```bash
psql "$DATABASE_URL" -f db/schema.sql
```

5. Run app:

```bash
python run.py
```

## Endpoints

### Health

- `GET /health`

### Create Product

- `POST /api/products`
- Example payload:

```json
{
  "company_id": "company-uuid",
  "name": "Widget",
  "sku": "wdg-001",
  "price": "12.50",
  "warehouse_id": "warehouse-uuid",
  "initial_quantity": 50,
  "low_stock_threshold": 10,
  "description": "Optional text",
  "product_type": "standard",
  "is_bundle": false
}
```

- Returns `201 Created` with created product details.

### Low Stock Alerts

- `GET /api/companies/<company_id>/alerts/low-stock`
- Uses rolling sales window (`SALES_WINDOW_DAYS`, default 30 days).
- Returns products under threshold with supplier recommendation.

## Tests

Run:

```bash
pytest -q
```

## Notes

- Product creation uses a single transaction and `flush()` to avoid partial writes.
- Low-stock query intentionally filters to products with recent sales to reduce dead-stock noise.
- Supplier selection prefers `is_preferred = true`, then falls back to earliest linked supplier.
