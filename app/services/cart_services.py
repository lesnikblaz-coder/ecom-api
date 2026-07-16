from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import cart_repository, product_repository
from app.models import Cart, CartItem
from app.exceptions import ProductNotFoundError, InsufficientStockError, CartItemNotFoundError, CartNotFoundError
from app.logging_config import logger
from app.database import transaction

async def require_cart_item(db: AsyncSession, cart_id: int, cart_item_id: int) -> CartItem:
    cart_item = await cart_repository.cart_item_get_by_id(db, cart_id, cart_item_id)

    if not cart_item:
        raise CartItemNotFoundError("Cart item doesnt exist.")

    return cart_item

async def cart_get_or_create(db: AsyncSession, user_id: int) -> Cart:
    cart = await cart_repository.cart_get_by_user(db, user_id)
    if not cart:
        cart = Cart(user_id=user_id)
        cart = await cart_repository.cart_create(db, cart)
    return cart

async def cart_get(db: AsyncSession, user_id: int) -> Cart:
    cart = await cart_repository.cart_get_by_user(db, user_id)
    if not cart:
        raise CartNotFoundError("Cart doesn't exist.")
    return cart

async def add_to_cart(db: AsyncSession, user_id: int, product_id: int, quantity_to_add: int) -> CartItem:
    async with transaction(db):
        cart = await cart_get_or_create(db, user_id)

        product = await product_repository.product_get(db, product_id)
        if not product:
            raise ProductNotFoundError("Product not found.")

        # checks if item already in cart
        existing_item = await cart_repository.cart_item_get_by_product(db, cart.cart_id, product_id)

        # check if enough stock exists
        new_quantity = quantity_to_add
        if existing_item:
            new_quantity += existing_item.quantity
        if new_quantity > product.quantity:
            raise InsufficientStockError("Not enough stock available.")

        # if item exists and stock valid, change current quantity to current+new_quantity
        if existing_item:
            existing_item.quantity = new_quantity

            logger.info(
                "Updated cart item %s in cart %s quantity=%s",
                existing_item.cart_item_id,
                cart.cart_id,
                existing_item.quantity
            )

            return await cart_repository.cart_item_save(db=db, cart_item=existing_item)

        # create new cart item
        cart_item = CartItem(cart_id=cart.cart_id, product_id=product_id, quantity=new_quantity)
        logger.info("Product %s added to cart %s quantity=%s", product_id, cart.cart_id, new_quantity)
        return await cart_repository.cart_item_save(db, cart_item)

async def cart_item_update(db: AsyncSession, user_id: int, cart_item_id: int, new_quantity: int) -> CartItem:
    async with transaction(db):
        cart = await cart_get_or_create(db, user_id)

        cart_item = await require_cart_item(db, cart.cart_id, cart_item_id)

        if new_quantity > cart_item.product.quantity:
            raise InsufficientStockError("Not enough stock available.")

        cart_item.quantity = new_quantity
        logger.info("Updated item %s quantity in cart %s", cart_item_id, cart.cart_id)
        return await cart_repository.cart_item_save(db, cart_item)

async def cart_item_delete(db: AsyncSession, user_id: int, cart_item_id: int) -> None:
    async with transaction(db):
        cart = await cart_get_or_create(db, user_id)
        cart_item = await require_cart_item(db, cart.cart_id, cart_item_id)
        logger.info("Deleted item %s from cart %s", cart_item_id, cart.cart_id)
        await cart_repository.cart_item_delete(db, cart_item)

async def cart_clear(db: AsyncSession, user_id: int) -> None:
    async with transaction(db):
        cart = await cart_get(db, user_id)
        logger.info("Cart %s cleared", cart.cart_id)
        await cart_repository.cart_clear(db, cart.cart_id)