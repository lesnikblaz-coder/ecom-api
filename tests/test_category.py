from sqlalchemy import select

from app.models import Category

def test_category_create(client, test_db):
    response = client.post("/categories", json={
        "name": "Test_Category"
    })

    assert response.status_code == 201

    category_id = response.json()["category_id"]
    category = (
        test_db.scalar(select(Category).where(Category.category_id == category_id))
    )

    assert category is not None
    assert category.category_id is not None
    assert category.name == "Test_Category"

def test_category_create_invalid(client):
    response = client.post("/categories", json={
        "name": "1"
    })

    assert response.status_code == 422

def test_category_create_duplicate_error(client, create_category):
    response = client.post("/categories", json={
        "name": "Test_Category"
    })

    assert response.json()["detail"] == "Category already exists."
    assert response.status_code == 409

def test_category_update(client, create_category):
    response = client.put(f'/categories/{create_category["category_id"]}', json={
        "name": "Updating_The_Name"
    })

    assert response.json()["name"] == "Updating_The_Name"
    assert response.status_code == 200

def test_category_update_invalid(client, create_category):
    response = client.put(f'/categories/{create_category["category_id"]}', json={
        "name": "1"
    })

    assert response.status_code == 422

def test_category_update_invalid_id(client):
    response = client.put(f'/categories/9999999', json={
        "name": "new name update"
    })

    assert response.status_code == 404

def test_category_delete(client, create_category, test_db):
    category_id = create_category['category_id']
    response = client.delete(f'/categories/{category_id}')

    assert response.status_code == 204
    category = test_db.scalar(select(Category).where(Category.category_id == category_id))
    assert category is None

def test_category_delete_invalid_id(client):
    response = client.delete(f'/categories/9999999')

    assert response.status_code == 404