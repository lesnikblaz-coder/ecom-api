from sqlalchemy import select

from app.models import CartItem, Cart

async def test_add_item_to_cart(client, create_product, test_db):
    response = await client.post("/cart/items", json={
        "product_id": create_product["product_id"],
        "quantity": 10
    })

    assert response.status_code == 201

    cart_item_id = response.json()["cart_item_id"]
    result = await test_db.execute(select(CartItem).where(CartItem.cart_item_id == cart_item_id))
    cart_item = result.scalar_one_or_none()

    assert cart_item.cart_id is not None
    assert cart_item.product_id is not None
    assert cart_item.quantity == 10

async def test_cart_item_quantity_update(client, create_cart_item, test_db):
    cart_item_id = create_cart_item["cart_item_id"]
    response = await client.put(f'/cart/items/{cart_item_id}', json={
        "quantity": 150
    })

    assert response.status_code == 200

    result = await test_db.execute(select(CartItem).where(CartItem.cart_item_id == cart_item_id))
    updated_cart_item = result.scalar_one()

    assert updated_cart_item.cart_item_id == cart_item_id
    assert updated_cart_item.quantity == 150

async def test_cart_item_invalid_quantity_update(client, create_cart_item):
    response = await client.put(f'/cart/items/{create_cart_item["cart_item_id"]}', json={
        "quantity": 99999999999999
    })

    assert response.status_code == 409

async def test_cart_item_delete(client, create_cart_item, test_db):
    cart_item_id = create_cart_item["cart_item_id"]
    response = await client.delete(f'/cart/items/{cart_item_id}')

    assert response.status_code == 204

    cart_item = await test_db.scalar(select(CartItem).where(CartItem.cart_item_id == cart_item_id))
    assert cart_item is None

async def test_cart_item_invalid_delete(client):
    response = await client.delete("/cart/items/99999999")
    assert response.status_code == 404

async def test_cart_clear(client, create_cart_item, test_db, auth_user):
    response = await client.delete("/cart")
    assert response.status_code == 204

    result_cart = await test_db.execute(select(Cart).where(Cart.cart_id == auth_user.user_id))
    cart = result_cart.scalar_one()

    result_cart_items = await test_db.execute(select(CartItem).where(CartItem.cart_id == cart.cart_id))
    cart_items = result_cart_items.scalars().all()
    assert cart_items == []