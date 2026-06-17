from app.models.orders import Order as OrderModel
from app.notifications.ws.manager import ws_manager
from app.notifications.ws.messages import OrderCreatedMessage
from app.ordering.services.notifier import OrderNotifier


class WebSocketOrderNotifier:
    """Адаптер: реализация OrderNotifier через ws_manager."""

    async def order_created(self, user_id: int, order: OrderModel) -> None:
        message: OrderCreatedMessage = {
            "type": "order_created",
            "order_id": order.id,
            "status": order.status,
            "total_amount": str(order.total_amount),
        }
        await ws_manager.notify_user(user_id, message)


_ws_notifier = WebSocketOrderNotifier()


def get_ws_order_notifier() -> OrderNotifier:
    return _ws_notifier
