from app.extensions import db
from app.models import Company, Warehouse


def seed_company_and_warehouse():
    company = Company(name="Acme Corp", slug="acme", plan="pro")
    db.session.add(company)
    db.session.flush()

    warehouse = Warehouse(company_id=company.id, name="Main WH")
    db.session.add(warehouse)
    db.session.commit()
    return company, warehouse


def test_create_product_returns_201(client):
    company, warehouse = seed_company_and_warehouse()

    response = client.post(
        "/api/products",
        json={
            "company_id": company.id,
            "name": "Widget",
            "sku": "wdg-001",
            "price": "12.50",
            "warehouse_id": warehouse.id,
            "initial_quantity": 20,
        },
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["product"]["sku"] == "WDG-001"


def test_create_product_validation_error(client):
    response = client.post("/api/products", json={"name": "Invalid"})

    assert response.status_code == 422
    data = response.get_json()
    assert "Missing fields" in data["error"]
