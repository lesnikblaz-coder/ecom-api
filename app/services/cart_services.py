from sqlalchemy.orm import Session

from app.repositories import cart_repository, product_repository
from app.models import Cart, CartItem
from app.exceptions import ProductNotFoundError, InsufficientStockError, CartItemNotFoundError, CartNotFoundError

def require_cart_item(db: Session, cart_id: int, cart_item_id: int) -> CartItem:
    cart_item = cart_repository.cart_item_get_by_id(db, cart_id, cart_item_id)

    if not cart_item:
        raise CartItemNotFoundError("Cart item doesnt exist.")

    return cart_item

def cart_get_or_create(db: Session, user_id: int) -> Cart:
    cart = cart_repository.cart_get_by_user(db, user_id)
    if not cart:
        cart = Cart(user_id=user_id)
        cart = cart_repository.cart_create(db, cart)
    return cart

def cart_get(db: Session, user_id: int) -> Cart:
    cart = cart_repository.cart_get_by_user(db, user_id)
    if not cart:
        raise CartNotFoundError("Cart doesn't exist.")
    return cart

def add_to_cart(db: Session, user_id: int, product_id: int, quantity_to_add: int) -> CartItem:
    cart = cart_get_or_create(db, user_id)

    product = product_repository.product_get(db, product_id)
    if not product:
        raise ProductNotFoundError("Product not found.")

    # checks if item already in cart
    existing_item = cart_repository.cart_item_get_by_product(db, cart.cart_id, product_id)

    # check if enough stock exists
    new_quantity = quantity_to_add
    if existing_item:
        new_quantity += existing_item.quantity
    if new_quantity > product.quantity:
        raise InsufficientStockError("Not enough stock available.")

    # if item exists and stock valid, change current quantity to current+new_quantity
    if existing_item:
        existing_item.quantity = new_quantity
        return cart_repository.cart_item_save(db=db, cart_item=existing_item)

    # else create new cart item
    cart_item = CartItem(cart_id=cart.cart_id, product_id=product_id, quantity=new_quantity)
    return cart_repository.cart_item_save(db, cart_item)

def cart_item_update(db: Session, user_id: int, cart_item_id: int, new_quantity: int) -> CartItem:
    cart = cart_get_or_create(db, user_id)

    cart_item = require_cart_item(db, cart.cart_id, cart_item_id)

    if new_quantity > cart_item.product.quantity:
        raise InsufficientStockError("Not enough stock available.")

    cart_item.quantity = new_quantity

    return cart_repository.cart_item_save(db, cart_item)

def cart_item_delete(db: Session, user_id: int, cart_item_id: int) -> None:
    cart = cart_get_or_create(db, user_id)
    cart_item = require_cart_item(db, cart.cart_id, cart_item_id)
    cart_repository.cart_item_delete(db, cart_item)

def cart_clear(db: Session, user_id: int) -> None:
    cart = cart_get(db, user_id)
    for item in cart.cart_items:
        cart_repository.cart_clear(db, item)