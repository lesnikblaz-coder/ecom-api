from sqlalchemy import select

from app.models import Order
from app.enums import OrderStatus

def test_order_create(client, create_cart_item, test_db, auth_user):
    response = client.post("/orders", json={
        "delivery_address": "123 Test Street, Test City"
    })

    assert response.status_code == 201
    order_id = response.json()["order_id"]
    order = test_db.scalar(select(Order).where(Order.order_id == order_id))

    assert order.order_id is not None
    assert order.user_id == auth_user.user_id
    assert order.total_price is not None
    assert order.status == OrderStatus.PENDING
    assert order.created_at is not None
    assert order.delivery_address == "123 Test Street, Test City"

def test_order_cancel(client, create_order, test_db):
    order_id = create_order["order_id"]
    response = client.post(f'/orders/{order_id}/cancel')
    assert response.status_code == 200

    order = test_db.scalar(select(Order).where(Order.order_id == order_id))
    assert order.status == OrderStatus.CANCELLED

def test_order_confirm(client, create_order, test_db, auth_user):
    order_id = create_order["order_id"]
    response = client.post(f'/orders/{order_id}/confirm', json={
        "user_id": auth_user.user_id
    })
    assert response.status_code == 200

    order = test_db.scalar(select(Order).where(Order.order_id == order_id))
    assert order.status == OrderStatus.CONFIRMED

def test_order_ship(client, create_order_confirmed, test_db, auth_user):
    order_id = create_order_confirmed["order_id"]
    response = client.post(f'/orders/{order_id}/ship', json={
        "user_id": auth_user.user_id
    })
    assert response.status_code == 200

    order = test_db.scalar(select(Order).where(Order.order_id == order_id))
    assert order.status == OrderStatus.SHIPPED

def test_order_ship_invalid(client, create_order, test_db, auth_user):
    order_id = create_order["order_id"]
    response = client.post(f'/orders/{order_id}/ship', json={
        "user_id": auth_user.user_id
    })
    assert response.status_code == 409

def test_order_delivered(client, create_order_shipped, test_db, auth_user):
    order_id = create_order_shipped["order_id"]
    response = client.post(f'/orders/{order_id}/delivered', json={
        "user_id": auth_user.user_id
    })
    assert response.status_code == 200

    order = test_db.scalar(select(Order).where(Order.order_id == order_id))
    assert order.status == OrderStatus.DELIVERED

def test_order_delivered_invalid(client, create_order, test_db, auth_user):
    order_id = create_order["order_id"]
    response = client.post(f'/orders/{order_id}/delivered', json={
        "user_id": auth_user.user_id
    })
    assert response.status_code == 409