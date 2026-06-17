from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog.deps import get_product_repository
from app.catalog.repositories.product_repository import ProductRepository
from app.db.deps import get_async_db
from app.ordering.repositories.cart_repository import CartRepository
from app.ordering.repositories.order_repository import OrderRepository
from app.ordering.services.cart_service import CartService
from app.ordering.services.notifier import OrderNotifier
from app.ordering.services.order_service import OrderService
from app.ordering.services.ws_notifier import get_ws_order_notifier


def get_order_repository(
    db: AsyncSession = Depends(get_async_db),
) -> OrderRepository:
    return OrderRepository(db)


def get_cart_repository(
    db: AsyncSession = Depends(get_async_db),
) -> CartRepository:
    return CartRepository(db)


def get_cart_service(
    cart_repo: CartRepository = Depends(get_cart_repository),
    product_repo: ProductRepository = Depends(get_product_repository),
) -> CartService:
    return CartService(cart_repo, product_repo)


def get_order_service(
    order_repo: OrderRepository = Depends(get_order_repository),
    cart_repo: CartRepository = Depends(get_cart_repository),
    notifier: OrderNotifier = Depends(get_ws_order_notifier),
) -> OrderService:
    return OrderService(order_repo, cart_repo, notifier)
