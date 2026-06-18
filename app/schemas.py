from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from decimal import Decimal

from app.enums import UserRole


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

class ProductResponse(BaseModel):
    model_config =  ConfigDict(from_attributes=True)

    product_id: int
    category_id: int
    name: str
    description: str | None = None
    price: Decimal
    quantity: int

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