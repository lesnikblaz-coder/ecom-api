from sqlalchemy import Integer, String, Boolean, ForeignKey, Enum, DECIMAL, UniqueConstraint, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal
from datetime import datetime

from app.database import Base
from app.enums import UserRole, OrderStatus
from app.exceptions import InvalidOrderStateError

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, default=UserRole.CUSTOMER)

    # 1:1 relationship
    cart: Mapped["Cart"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")

    orders: Mapped[list["Order"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Category(Base):
    __tablename__ = "categories"

    category_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)

    products: Mapped[list["Product"]] = relationship(back_populates="category")

class Product(Base):
    __tablename__ = "products"

    product_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.category_id"), nullable=False)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=True)
    price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    category: Mapped[Category] = relationship(back_populates="products")
    cart_items: Mapped[list["CartItem"]] = relationship(back_populates="product")
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="product")

class Cart(Base):
    __tablename__ = "carts"

    cart_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id"), unique=True, nullable=False)

    # cascade -> when cart gets deleted, include all its cart_items in delete
    cart_items: Mapped[list["CartItem"]] = relationship(back_populates="cart", cascade="all, delete-orphan")
    user: Mapped[User] = relationship(back_populates="cart")

class CartItem(Base):
    __tablename__ = "cart_items"

    # makes sure there is no duplicate CartItems
    __table_args__ = (
        UniqueConstraint("cart_id", "product_id"),
    )

    cart_item_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cart_id: Mapped[int] = mapped_column(Integer, ForeignKey("carts.cart_id"), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.product_id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    cart: Mapped[Cart] = relationship(back_populates="cart_items")
    product: Mapped[Product] = relationship(back_populates="cart_items")

class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id"), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), nullable=False,  default=OrderStatus.PENDING_PAYMENT)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    delivery_address: Mapped[str] = mapped_column(String, nullable=False)

    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")
    user: Mapped[User] = relationship(back_populates="orders")

    def cancel(self) -> None:
        if self.status not in (OrderStatus.PENDING_PAYMENT, OrderStatus.CONFIRMED):
            raise InvalidOrderStateError("Order in uncancellable state.")
        self.status = OrderStatus.CANCELLED

    def confirm(self) -> None:
        if self.status != OrderStatus.PENDING_PAYMENT:
            raise InvalidOrderStateError("Only pending orders can be confirmed.")
        self.status = OrderStatus.CONFIRMED

    def ship(self):
        if self.status != OrderStatus.CONFIRMED:
            raise InvalidOrderStateError("Only confirmed orders can be shipped.")
        self.status = OrderStatus.SHIPPED

    def delivered(self):
        if self.status != OrderStatus.SHIPPED:
            raise InvalidOrderStateError("Only shipped orders can be delivered.")
        self.status = OrderStatus.DELIVERED

class OrderItem(Base):
    __tablename__ = "order_items"

    order_item_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.order_id"), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.product_id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)

    order: Mapped[Order] = relationship(back_populates="order_items")
    product: Mapped[Product] = relationship(back_populates="order_items")