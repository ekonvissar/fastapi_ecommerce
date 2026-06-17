from fastapi import APIRouter, Depends, Query, status

from app.auth import get_current_user
from app.models.users import User as UserModel
from app.ordering.deps import get_order_service
from app.ordering.schemas.order import Order as OrderSchema
from app.ordering.schemas.order import OrderList
from app.ordering.services.order_service import OrderService

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)


@router.post(
    "/checkout", response_model=OrderSchema, status_code=status.HTTP_201_CREATED
)
async def checkout_order(
    current_user: UserModel = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
):
    return await service.checkout(user_id=current_user.id)


@router.get("/", response_model=OrderList)
async def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: UserModel = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
):
    orders, total = await service.list_orders(
        current_user.id, page=page, page_size=page_size
    )
    return OrderList(items=orders, total=total, page=page, page_size=page_size)


@router.get("/{order_id}", response_model=OrderSchema)
async def get_order(
    order_id: int,
    current_user: UserModel = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
):
    return await service.get_order(current_user.id, order_id)
