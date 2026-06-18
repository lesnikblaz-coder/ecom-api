from sqlalchemy.orm import Session

from app.repositories import cart_repository, product_repository
from app.models import Cart, CartItem
from app.exceptions import ProductNotFoundError, InsufficientStockError

def cart_get_or_create(db: Session, user_id: int) -> Cart:
    cart = cart_repository.cart_get_by_user(db, user_id)
    if not cart:
        cart = Cart(user_id=user_id)
        cart = cart_repository.cart_create(db, cart)
    return cart

def add_to_cart(db: Session, user_id: int, product_id: int, quantity: int) -> CartItem:
    cart = cart_get_or_create(db, user_id)

    product = product_repository.product_get(db, product_id)
    if not product:
        raise ProductNotFoundError("Product not found.")

    # checks if item already in cart
    existing_item = cart_repository.cart_item_get(db, cart.cart_id, product_id)
    
    # check if enough stock exists
    new_quantity = quantity
    if existing_item:
        new_quantity += existing_item.quantity
    if new_quantity > product.quantity:
        raise InsufficientStockError("Not enough stock available.")

    # if item exists and stock valid, change current quantity to current+new_quantity
    if existing_item:
        existing_item.quantity = new_quantity
        return cart_repository.cart_item_save(db=db, cart_item=existing_item)

    # else create new cart item
    cart_item = CartItem(cart_id=cart.cart_id, product_id=product_id, quantity=quantity)
    return cart_repository.cart_item_save(db, cart_item)