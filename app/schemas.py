from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from decimal import Decimal
from datetime import datetime

from app.enums import UserRole, OrderStatus, PaymentStatus


# USER
class UserLoginRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    email: EmailStr
    is_active: bool
    role: UserRole

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    is_active: bool | None = None
    role: UserRole | None = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserIdRequest(BaseModel):
    user_id: int


# CATEGORY
class CategoryRequest(BaseModel):
    name: str = Field(min_length=3, max_length=30)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, name):
        return name.strip().title()

class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category_id: int
    name: str

class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=30)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, name):
        if name is None:
            return None
        return name.strip().title()


# PRODUCT
class ProductRequest(BaseModel):
    category_id: int
    name: str = Field(min_length=3, max_length=30)
    description: str = Field(max_length=200)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    quantity: int = Field(ge=0, le=10000)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, name):
        return name.strip().capitalize()

class ProductFilters(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)

    category: str | None = None
    min_price: float | None = None
    max_price: float | None = None
    search: str | None = None
    in_stock: bool | None = None

    #sort
    #order

class ProductResponse(BaseModel):
    model_config =  ConfigDict(from_attributes=True)

    product_id: int
    category_id: int
    name: str
    description: str | None = None
    price: Decimal
    quantity: int

class PaginatedProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    products: list[ProductResponse]
    page: int
    limit: int
    total: int
    pages: int
    has_next: bool
    has_previous: bool
    next_page: int | None = None
    previous_page: int | None = None

class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=30)
    description: str | None = Field(default=None, max_length=200)
    price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    quantity: int | None = Field(default=None, ge=0, le=10000)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, name):
        if name is None:
            return None
        return name.strip().capitalize()


# CART
class CartItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cart_item_id: int
    product: ProductResponse
    quantity: int

class CartResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cart_id: int
    user_id: int
    cart_items: list[CartItemResponse]

class CartItemRequest(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)

class CartItemQuantityUpdate(BaseModel):
    quantity: int = Field(gt=0)


# ORDER
class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_item_id: int
    order_id: int
    product: ProductResponse
    quantity: int
    unit_price: Decimal

class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: int
    user_id: int
    total_price: Decimal
    status: OrderStatus
    created_at: datetime
    delivery_address: str
    order_items: list[OrderItemResponse]

class OrderCreate(BaseModel):
    delivery_address: str = Field(min_length=5)


# PAYMENT
class PaymentCreate(BaseModel):
    order_id: int = Field(ge=1)

class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    payment_id: int
    order_id: int
    amount: Decimal
    status: PaymentStatus
    provider: str
    created_at: datetime