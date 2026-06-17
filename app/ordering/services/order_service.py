from decimal import Decimal

from app.models.orders import Order as OrderModel
from app.models.orders import OrderItem as OrderItemModel
from app.ordering.repositories.cart_repository import CartRepository
from app.ordering.repositories.order_repository import OrderRepository
from app.ordering.services.notifier import OrderNotifier
from app.shared.exceptions import (
    CartEmptyError,
    NotEnoughStockError,
    OrderLoadError,
    OrderNotFoundError,
    ProductPriceMissingError,
    ProductUnavailableError,
)


class OrderService:
    """Бизнес-логика заказов: checkout, список, детали."""

    def __init__(
        self,
        order_repo: OrderRepository,
        cart_repo: CartRepository,
        notifier: OrderNotifier,
    ) -> None:
        self._orders = order_repo
        self._cart = cart_repo
        self._notifier = notifier

    async def checkout(self, user_id: int) -> OrderModel:
        cart_items = await self._cart.get_items_for_user(user_id)
        if not cart_items:
            raise CartEmptyError

        order = OrderModel(user_id=user_id)
        total_amount = Decimal(0)

        for cart_item in cart_items:
            product = cart_item.product
            if not product or not product.is_active:
                raise ProductUnavailableError(cart_item.product_id)
            if product.stock < cart_item.quantity:
                raise NotEnoughStockError(product.name)

            unit_price = product.price
            if unit_price is None:
                raise ProductPriceMissingError(product.name)

            total_price = unit_price * cart_item.quantity
            total_amount += total_price

            order.items.append(
                OrderItemModel(
                    product_id=cart_item.product_id,
                    quantity=cart_item.quantity,
                    unit_price=unit_price,
                    total_price=total_price,
                )
            )
            product.stock -= cart_item.quantity

        order.total_amount = total_amount
        await self._orders.add(order)
        await self._cart.clear_for_user(user_id)
        await self._orders.commit()

        created_order = await self._orders.get_by_id_with_items(order.id)
        if not created_order:
            raise OrderLoadError

        await self._notifier.order_created(user_id, created_order)
        return created_order

    async def list_orders(
        self, user_id: int, *, page: int, page_size: int
    ) -> tuple[list[OrderModel], int]:
        total = await self._orders.count_for_user(user_id)
        orders = await self._orders.list_for_user(
            user_id, page=page, page_size=page_size
        )
        return orders, total

    async def get_order(self, user_id: int, order_id: int) -> OrderModel:
        order = await self._orders.get_by_id_with_items(order_id)
        if not order or order.user_id != user_id:
            raise OrderNotFoundError
        return order
