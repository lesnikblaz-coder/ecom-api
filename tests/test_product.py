from sqlalchemy import select

from app.models import Product

async def test_product_create(client, create_category, test_db):
    response = await client.post("/products", json={
        "category_id": create_category["category_id"],
        "name": "test_product_name",
        "description": "test_description",
        "price": "19.99",
        "quantity": 999
    })

    assert response.status_code == 201

    product_id = response.json()["product_id"]
    result = await test_db.execute(select(Product).where(Product.product_id == product_id))
    product = result.scalar_one_or_none()

    assert product.product_id is not None
    assert product.category_id is not None
    assert product.name == "Test_product_name"
    assert product.description == "test_description"

async def test_product_create_invalid(client, create_category):
    response = await client.post("/products", json={
        "category_id": create_category["category_id"],
        "name": "test_product_name",
        "description": "test_description"
    })

    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Field required"
    assert response.json()["detail"][1]["msg"] == "Field required"

async def test_product_update(client, create_product, test_db):
    product_id = create_product["product_id"]
    response = await client.put(f"/products/{product_id}", json={
        "name": "test product name updating",
        "quantity": 134
    })

    assert response.status_code == 200

    result = await test_db.execute(select(Product).where(Product.product_id == product_id))
    product = result.scalar_one_or_none()

    assert product.name == "Test product name updating"
    assert product.quantity == 134

async def test_product_update_invalid(client, create_product):
    product_id = create_product["product_id"]
    response = await client.put(f"/products/{product_id}", json={
        "name": "test product name updating",
        "quantity": -5
    })

    assert response.status_code == 422

async def test_product_update_invalid_id(client):
    response = await client.put("/products/9999999", json={
        "quantity": 10
    })

    assert response.status_code == 404

async def test_product_delete(client, create_product):
    product_id = create_product["product_id"]
    response = await client.delete(f"/products/{product_id}")

    assert response.status_code == 204

async def test_product_delete_invalid_id(client):
    response = await client.delete("/products/9999999")

    assert response.status_code == 404