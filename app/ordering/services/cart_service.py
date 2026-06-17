from decimal import Decimal

from app.catalog.repositories.product_repository import ProductRepository
from app.models.cart_items import CartItem as CartItemModel
from app.ordering.repositories.cart_repository import CartRepository
from app.ordering.schemas.cart import Cart as CartSchema
from app.ordering.schemas.cart import CartItemCreate, CartItemUpdate
from app.shared.exceptions import CartItemNotFoundError, ProductNotFoundError


class CartService:
    """Бизнес-логика корзины: просмотр, добавление, изменение, очистка."""

    def __init__(
        self,
        cart_repo: CartRepository,
        product_repo: ProductRepository,
    ) -> None:
        self._cart = cart_repo
        self._products = product_repo

    async def _ensure_product_available(self, product_id: int) -> None:
        product = await self._products.get_active_by_id(product_id)
        if not product:
            raise ProductNotFoundError(product_id)

    async def get_cart(self, user_id: int) -> CartSchema:
        items = await self._cart.get_items_for_user(user_id)
        total_quantity = sum(item.quantity for item in items)
        price_items = (
            Decimal(item.quantity)
            * (item.product.price if item.product.price is not None else Decimal("0"))
            for item in items
        )
        total_price = sum(price_items, Decimal("0"))
        return CartSchema(
            user_id=user_id,
            items=items,
            total_quantity=total_quantity,
            total_price=total_price,
        )

    async def add_item(self, user_id: int, payload: CartItemCreate) -> CartItemModel:
        await self._ensure_product_available(payload.product_id)

        cart_item = await self._cart.get_item_for_user(user_id, payload.product_id)
        if cart_item:
            cart_item.quantity += payload.quantity
        else:
            cart_item = CartItemModel(
                user_id=user_id,
                product_id=payload.product_id,
                quantity=payload.quantity,
            )
            await self._cart.add(cart_item)

        await self._cart.commit()
        updated = await self._cart.get_item_for_user(user_id, payload.product_id)
        if not updated:
            raise CartItemNotFoundError(payload.product_id)
        return updated

    async def update_item(
        self, user_id: int, product_id: int, payload: CartItemUpdate
    ) -> CartItemModel:
        await self._ensure_product_available(product_id)

        cart_item = await self._cart.get_item_for_user(user_id, product_id)
        if not cart_item:
            raise CartItemNotFoundError(product_id)

        cart_item.quantity = payload.quantity
        await self._cart.commit()
        updated = await self._cart.get_item_for_user(user_id, product_id)
        if not updated:
            raise CartItemNotFoundError(product_id)
        return updated

    async def remove_item(self, user_id: int, product_id: int) -> None:
        cart_item = await self._cart.get_item_for_user(user_id, product_id)
        if not cart_item:
            raise CartItemNotFoundError(
                product_id,
                detail=f"Product with id {product_id} not found",
            )

        await self._cart.delete(cart_item)
        await self._cart.commit()

    async def clear(self, user_id: int) -> None:
        await self._cart.clear_for_user(user_id)
        await self._cart.commit()
