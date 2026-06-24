from sqlalchemy import select

from app.models import Product

def test_product_create(client, create_category, test_db):
    response = client.post("/products", json={
        "category_id": create_category["category_id"],
        "name": "test_product_name",
        "description": "test_description",
        "price": "19.99",
        "quantity": 999
    })

    assert response.status_code == 201

    product_id = response.json()["product_id"]
    product = test_db.scalar(select(Product).where(Product.product_id == product_id))

    assert product.product_id is not None
    assert product.category_id is not None
    assert product.name == "Test_product_name"
    assert product.description == "test_description"

def test_product_create_invalid(client, create_category):
    response = client.post("/products", json={
        "category_id": create_category["category_id"],
        "name": "test_product_name",
        "description": "test_description"
    })

    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Field required"
    assert response.json()["detail"][1]["msg"] == "Field required"

def test_product_update(client, create_product, test_db):
    product_id = create_product["product_id"]
    response = client.put(f"/products/{product_id}", json={
        "name": "test product name updating",
        "quantity": 134
    })

    assert response.status_code == 200

    product = test_db.scalar(select(Product).where(Product.product_id == product_id))
    assert product.name == "Test product name updating"
    assert product.quantity == 134

def test_product_update_invalid(client, create_product):
    product_id = create_product["product_id"]
    response = client.put(f"/products/{product_id}", json={
        "name": "test product name updating",
        "quantity": -5
    })

    assert response.status_code == 422

def test_product_update_invalid_id(client):
    response = client.put("/products/9999999", json={
        "quantity": 10
    })

    assert response.status_code == 404

def test_product_delete(client, create_product):
    product_id = create_product["product_id"]
    response = client.delete(f"/products/{product_id}")

    assert response.status_code == 204

def test_product_delete_invalid_id(client):
    response = client.delete("/products/9999999")

    assert response.status_code == 404