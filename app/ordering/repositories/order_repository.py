from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.utils import get_by_id
from app.models.orders import Order as OrderModel
from app.models.orders import OrderItem as OrderItemModel

_ORDER_WITH_ITEMS = (
    selectinload(OrderModel.items).selectinload(OrderItemModel.product),
)


class OrderRepository:
    """Доступ к заказам. Только SQL — без бизнес-правил."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id_with_items(self, order_id: int) -> OrderModel | None:
        return await get_by_id(
            self._db,
            OrderModel,
            order_id,
            options=_ORDER_WITH_ITEMS,
        )

    async def add(self, order: OrderModel) -> None:
        self._db.add(order)

    async def commit(self) -> None:
        await self._db.commit()

    async def count_for_user(self, user_id: int) -> int:
        return (
            await self._db.scalar(
                select(func.count(OrderModel.id)).where(OrderModel.user_id == user_id)
            )
        ) or 0

    async def list_for_user(
        self, user_id: int, *, page: int, page_size: int
    ) -> list[OrderModel]:
        result = await self._db.scalars(
            select(OrderModel)
            .options(_ORDER_WITH_ITEMS)
            .where(OrderModel.user_id == user_id)
            .order_by(OrderModel.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result)
