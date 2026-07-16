from sqlalchemy import select

from app.models import Order
from app.enums import OrderStatus

async def test_checkout_success(client, create_cart_item, test_db, auth_user):
    response = await client.post("/orders", json={
        "delivery_address": "123 Test Street, Test City"
    })

    assert response.status_code == 201
    order_id = response.json()["order_id"]
    result = await test_db.execute(select(Order).where(Order.order_id == order_id))
    order = result.scalar_one_or_none()

    assert order.order_id is not None
    assert order.user_id == auth_user.user_id
    assert order.total_price is not None
    assert order.status == OrderStatus.CONFIRMED
    assert order.created_at is not None
    assert order.delivery_address == "123 Test Street, Test City"

async def test_order_cancel(client, create_order, test_db):
    order_id = create_order["order_id"]
    response = await client.post(f'/orders/{order_id}/cancel')
    assert response.status_code == 200

    result = await test_db.execute(select(Order).where(Order.order_id == order_id))
    order = result.scalar_one_or_none()
    assert order.status == OrderStatus.CANCELLED

async def test_order_ship(client, create_order, test_db, auth_user):
    order_id = create_order["order_id"]
    response = await client.post(f'/orders/{order_id}/ship', json={
        "user_id": auth_user.user_id
    })
    assert response.status_code == 200

    result = await test_db.execute(select(Order).where(Order.order_id == order_id))
    order = result.scalar_one_or_none()
    assert order.status == OrderStatus.SHIPPED

async def test_order_ship_invalid(client, create_order_pending, test_db, auth_user):
    order_id = create_order_pending["order_id"]
    response = await client.post(f'/orders/{order_id}/ship', json={
        "user_id": auth_user.user_id
    })
    assert response.status_code == 409

async def test_order_delivered(client, create_order_shipped, test_db, auth_user):
    order_id = create_order_shipped["order_id"]
    response = await client.post(f'/orders/{order_id}/delivered', json={
        "user_id": auth_user.user_id
    })
    assert response.status_code == 200

    result = await test_db.execute(select(Order).where(Order.order_id == order_id))
    order = result.scalar_one_or_none()
    assert order.status == OrderStatus.DELIVERED

async def test_order_delivered_invalid(client, create_order, test_db, auth_user):
    order_id = create_order["order_id"]
    response = await client.post(f'/orders/{order_id}/delivered', json={
        "user_id": auth_user.user_id
    })
    assert response.status_code == 409