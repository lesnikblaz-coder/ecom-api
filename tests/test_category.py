from sqlalchemy import select

from app.models import Category

async def test_category_create(client, test_db):
    response = await client.post("/categories", json={
        "name": "Test_Category"
    })

    assert response.status_code == 201

    category_id = response.json()["category_id"]
    result = await test_db.execute(select(Category).where(Category.category_id == category_id))
    category = result.scalar_one()

    assert category is not None
    assert category.category_id is not None
    assert category.name == "Test_Category"

async def test_category_create_invalid(client):
    response = await client.post("/categories", json={
        "name": "1"
    })

    assert response.status_code == 422

async def test_category_create_duplicate_error(client, create_category):
    response = await client.post("/categories", json={
        "name": "Test_Category"
    })

    assert response.json()["detail"] == "Category already exists."
    assert response.status_code == 409

async def test_category_update(client, create_category):
    response = await client.put(f'/categories/{create_category["category_id"]}', json={
        "name": "Updating_The_Name"
    })

    assert response.json()["name"] == "Updating_The_Name"
    assert response.status_code == 200

async def test_category_update_invalid(client, create_category):
    response = await client.put(f'/categories/{create_category["category_id"]}', json={
        "name": "1"
    })

    assert response.status_code == 422

async def test_category_update_invalid_id(client):
    response = await client.put(f'/categories/9999999', json={
        "name": "new name update"
    })

    assert response.status_code == 404

async def test_category_delete(client, create_category, test_db):
    category_id = create_category['category_id']
    response = await client.delete(f'/categories/{category_id}')

    assert response.status_code == 204
    result = await test_db.execute(select(Category).where(Category.category_id == category_id))
    category = result.scalar_one_or_none()
    assert category is None

async def test_category_delete_invalid_id(client):
    response = await client.delete(f'/categories/9999999')

    assert response.status_code == 404