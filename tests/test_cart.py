from sqlalchemy import select

from app.models import CartItem

def test_add_item_to_cart(client, create_product, test_db):
    response = client.post("/cart/items", json={
        "product_id": create_product["product_id"],
        "quantity": 10
    })

    assert response.status_code == 201

    cart_item_id = response.json()["cart_item_id"]
    cart_item = test_db.scalar(select(CartItem).where(CartItem.cart_item_id == cart_item_id))

    assert cart_item.cart_id is not None
    assert cart_item.product_id is not None
    assert cart_item.quantity == 10

def test_cart_item_quantity_update(client, create_cart_item, test_db):
    cart_item_id = create_cart_item["cart_item_id"]
    response = client.put(f'/cart/items/{cart_item_id}', json={
        "quantity": 150
    })

    assert response.status_code == 200

    updated_cart_item = test_db.scalar(select(CartItem).where(CartItem.cart_item_id == cart_item_id))
    assert updated_cart_item.cart_item_id == cart_item_id
    assert updated_cart_item.quantity == 150

def test_cart_item_invalid_quantity_update(client, create_cart_item):
    response = client.put(f'/cart/items/{create_cart_item["cart_item_id"]}', json={
        "quantity": 99999999999999
    })

    assert response.status_code == 409

def test_cart_item_delete(client, create_cart_item, test_db):
    cart_item_id = create_cart_item["cart_item_id"]
    response = client.delete(f'/cart/items/{cart_item_id}')

    assert response.status_code == 204

    cart_item = test_db.scalar(select(CartItem).where(CartItem.cart_item_id == cart_item_id))
    assert cart_item is None

def test_cart_item_invalid_delete(client):
    response = client.delete("/cart/items/99999999")
    assert response.status_code == 404

def test_cart_clear(client, create_cart_item, test_db, auth_user):
    response = client.delete("/cart")
    assert response.status_code == 204

    cart_items = test_db.scalars(select(CartItem).where(CartItem.cart_id == auth_user.cart.cart_id)).all()
    assert cart_items == []