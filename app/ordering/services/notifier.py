from typing import Protocol

from app.models.orders import Order as OrderModel


class OrderNotifier(Protocol):
    """Порт: сервис не знает про WebSocket, только «уведомить о заказе»."""

    async def order_created(self, user_id: int, order: OrderModel) -> None: ...
