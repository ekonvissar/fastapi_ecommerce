from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cart_items import CartItem as CartItemModel
from app.models.products import Product as ProductModel

_CART_ITEM_WITH_PRODUCT = (
    selectinload(CartItemModel.product).selectinload(ProductModel.category),
)


class CartRepository:
    """Доступ к корзине. Только SQL — без бизнес-правил."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_items_for_user(self, user_id: int) -> list[CartItemModel]:
        result = await self._db.scalars(
            select(CartItemModel)
            .options(*_CART_ITEM_WITH_PRODUCT)
            .where(CartItemModel.user_id == user_id)
            .order_by(CartItemModel.id)
        )
        return list(result.all())

    async def get_item_for_user(
        self, user_id: int, product_id: int
    ) -> CartItemModel | None:
        result = await self._db.scalars(
            select(CartItemModel)
            .options(*_CART_ITEM_WITH_PRODUCT)
            .where(
                CartItemModel.user_id == user_id,
                CartItemModel.product_id == product_id,
            )
        )
        return result.first()

    async def add(self, cart_item: CartItemModel) -> None:
        self._db.add(cart_item)

    async def delete(self, cart_item: CartItemModel) -> None:
        await self._db.delete(cart_item)

    async def clear_for_user(self, user_id: int) -> None:
        await self._db.execute(
            delete(CartItemModel).where(CartItemModel.user_id == user_id)
        )

    async def commit(self) -> None:
        await self._db.commit()
