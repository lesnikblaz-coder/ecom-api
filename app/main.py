from fastapi import FastAPI, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from collections.abc import Sequence

from app import schemas
from app import auth
from app import models

from app.database import get_db
from app.exception_handlers import register_exception_handlers
from app.services.payment_services import PaymentService
from app.dependencies import get_payment_service
from app.services import (
    auth_services,
    user_services,
    category_services,
    product_services,
    cart_services,
    order_services,
    payment_services)

app = FastAPI()
register_exception_handlers(app)

db_session = Annotated[AsyncSession, Depends(get_db)]

@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {"status": "ok"}

# USER AUTH
@app.post("/auth/register", response_model=schemas.TokenResponse)
async def register(data: schemas.UserLoginRegister, db: db_session) -> schemas.TokenResponse:
    return await auth_services.register(db, data.email, data.password)

@app.post("/auth/login", response_model=schemas.TokenResponse)
async def login(data: schemas.UserLoginRegister, db: db_session) -> schemas.TokenResponse:
    return await auth_services.login(db, data.email, data.password)

@app.post("/auth/token", response_model=schemas.TokenResponse)
async def token(db: db_session, form_data: OAuth2PasswordRequestForm = Depends()) -> schemas.TokenResponse:
    return await auth_services.login(db, form_data.username, form_data.password)


# USERS (admin+)
@app.get("/users", response_model=list[schemas.UserResponse])
async def users_get(db: db_session, _: models.User = Depends(auth.require_admin)) -> Sequence[models.User]:
    return await user_services.users_get(db)

@app.get("/users/{user_id}", response_model=schemas.UserResponse)
async def user_get(user_id: int, db: db_session, _: models.User = Depends(auth.require_admin)) -> models.User:
    return await user_services.user_get(db, user_id)

@app.put("/users/{user_id}", response_model=schemas.UserResponse)
async def user_update(user_id: int, data: schemas.UserUpdate, db: db_session, _: models.User = Depends(auth.require_admin)) -> models.User:
    return await user_services.user_update(db, user_id, data)

@app.delete("/users/{user_id}", status_code=204)
async def user_delete(user_id: int, db: db_session, _: models.User = Depends(auth.require_admin)) -> None:
    await user_services.user_delete(db, user_id)


# CATEGORIES (staff+)
@app.post("/categories", response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED)
async def category_create(db: db_session, data: schemas.CategoryRequest, _: models.User = Depends(auth.require_staff)) -> models.Category:
    return await category_services.category_create(db, data.name)

@app.get("/categories", response_model=list[schemas.CategoryResponse])
async def categories_get(db: db_session, _: models.User = Depends(auth.require_staff)) -> Sequence[models.Category]:
    return await category_services.categories_get(db)

@app.get("/categories/{category_id}", response_model=schemas.CategoryResponse)
async def category_get(category_id: int, db: db_session, _: models.User = Depends(auth.require_staff)) -> models.Category:
    return await category_services.category_get(db, category_id)

@app.put("/categories/{category_id}", response_model=schemas.CategoryResponse)
async def category_update(category_id: int, db: db_session, data: schemas.CategoryUpdate, _: models.User = Depends(auth.require_staff)) -> models.Category:
    return await category_services.category_update(db, category_id, data)

@app.delete("/categories/{category_id}", status_code=204)
async def category_delete(category_id: int, db: db_session, _: models.User = Depends(auth.require_staff)) -> None:
    await category_services.category_delete(db, category_id)


# PRODUCTS
@app.post("/products", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED)  # staff+
async def product_create(db: db_session, data: schemas.ProductRequest, _: models.User = Depends(auth.require_staff)) -> models.Product:
    return await product_services.product_create(
        db=db,
        category_id=data.category_id,
        name=data.name,
        description=data.description,
        price=data.price,
        quantity=data.quantity
    )

@app.get("/products", response_model=schemas.PaginatedProductResponse)  # authenticated+
async def products_get(db: db_session, _: models.User = Depends(auth.get_current_user), filters: schemas.ProductFilters = Depends()) -> schemas.PaginatedProductResponse:
    return await product_services.products_get(db, filters)

@app.get("/products/{product_id}", response_model=schemas.ProductResponse)  # authenticated+
async def product_get(product_id: int, db: db_session, _: models.User = Depends(auth.get_current_user)) -> models.Product:
    return await product_services.product_get(db, product_id)

@app.put("/products/{product_id}", response_model=schemas.ProductResponse)  # staff+
async def product_update(product_id: int, db: db_session, data: schemas.ProductUpdate, _: models.User = Depends(auth.require_staff)) -> models.Product:
    return await product_services.product_update(db, product_id, data)

@app.delete("/products/{product_id}", status_code=204)  # staff+
async def product_delete(product_id: int, db: db_session, _: models.User = Depends(auth.require_staff)) -> None:
    await product_services.product_delete(db, product_id)


# CARTS
@app.get("/cart", response_model=schemas.CartResponse)
async def cart_get(db: db_session, current_user: models.User = Depends(auth.get_current_user)) -> models.Cart:
    return await cart_services.cart_get_or_create(db, current_user.user_id)

@app.delete("/cart", status_code=204)
async def cart_clear(db: db_session, current_user: models.User = Depends(auth.get_current_user)) -> None:
    await cart_services.cart_clear(db, current_user.user_id)

@app.post("/cart/items", response_model=schemas.CartItemResponse, status_code=status.HTTP_201_CREATED)
async def add_to_cart(db: db_session, data: schemas.CartItemRequest, current_user: models.User = Depends(auth.get_current_user)) -> models.CartItem:
    return await cart_services.add_to_cart(db, current_user.user_id, data.product_id, data.quantity)

@app.put("/cart/items/{cart_item_id}", response_model=schemas.CartItemResponse)
async def cart_item_quantity_update(db: db_session, cart_item_id: int, data: schemas.CartItemQuantityUpdate, current_user: models.User = Depends(auth.get_current_user)) -> models.CartItem:
    return await cart_services.cart_item_update(db, current_user.user_id, cart_item_id, data.quantity)

@app.delete("/cart/items/{cart_item_id}", status_code=204)
async def cart_item_delete(db: db_session, cart_item_id: int, current_user: models.User = Depends(auth.get_current_user)) -> None:
    await cart_services.cart_item_delete(db, current_user.user_id, cart_item_id)


# ORDERS
@app.get("/orders", response_model=list[schemas.OrderResponse])
async def orders_get(db: db_session, current_user: models.User = Depends(auth.get_current_user)) -> Sequence[models.Order]:
    return await order_services.orders_get_by_user(db, current_user.user_id)

@app.post("/orders", response_model=schemas.OrderResponse, status_code=status.HTTP_201_CREATED)
async def order_create(db: db_session, data: schemas.OrderCreate, current_user: models.User = Depends(auth.get_current_user), payment_service: PaymentService = Depends(get_payment_service)):
    return await order_services.checkout(db, current_user.user_id, data.delivery_address, payment_service)

@app.get("/orders/{order_id}", response_model=schemas.OrderResponse)
async def order_get(db: db_session, order_id: int, current_user: models.User = Depends(auth.get_current_user)):
    return await order_services.order_get_by_user(db, order_id, current_user.user_id)

@app.delete("/orders/{order_id}", status_code=204)
async def order_delete(db: db_session, order_id: int, _: models.User = Depends(auth.require_admin)) -> None:
    await order_services.order_delete(db, order_id)

@app.post("/orders/{order_id}/cancel", response_model=schemas.OrderResponse)
async def order_cancel(db: db_session, order_id: int, current_user: models.User = Depends(auth.get_current_user)) -> models.Order:
    return await order_services.cancel(db, order_id, current_user.user_id)

@app.post("/orders/{order_id}/ship", response_model=schemas.OrderResponse) # STAFF +
async def order_ship(db: db_session, order_id: int, data: schemas.UserIdRequest, _: models.User = Depends(auth.require_staff)) -> models.Order:
    return await order_services.ship(db, order_id, data.user_id)

@app.post("/orders/{order_id}/delivered", response_model=schemas.OrderResponse) # STAFF +
async def order_delivered(db: db_session, order_id: int, data: schemas.UserIdRequest, _: models.User = Depends(auth.require_staff)) -> models.Order:
    return await order_services.delivered(db, order_id, data.user_id)

@app.get("/orders/{order_id}/payments", response_model=list[schemas.PaymentResponse])
async def order_get_payments(db: db_session, order_id: int, _: models.User = Depends(auth.get_current_user)) -> Sequence[models.Payment]:
    return await payment_services.payments_for_order(db, order_id)


# PAYMENTS
@app.post("/payments/{order_id}/retry", response_model=schemas.PaymentResponse)
async def payment_retry(db: db_session, order_id: int, current_user: models.User = Depends(auth.get_current_user), payment_service: PaymentService = Depends(get_payment_service)) -> models.Payment:
    return await payment_service.payment_retry(db, order_id, current_user.user_id)