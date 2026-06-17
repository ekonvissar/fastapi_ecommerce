from fastapi import APIRouter, Depends, Response, status

from app.auth import get_current_user
from app.models.users import User as UserModel
from app.ordering.deps import get_cart_service
from app.ordering.schemas.cart import Cart as CartSchema
from app.ordering.schemas.cart import CartItem as CartItemSchema
from app.ordering.schemas.cart import CartItemCreate, CartItemUpdate
from app.ordering.services.cart_service import CartService

router = APIRouter(
    prefix="/cart",
    tags=["cart"],
)

items_router = APIRouter(prefix="/items")


@router.get("/", response_model=CartSchema)
async def get_cart(
    current_user: UserModel = Depends(get_current_user),
    service: CartService = Depends(get_cart_service),
):
    return await service.get_cart(current_user.id)


@items_router.post(
    "/", response_model=CartItemSchema, status_code=status.HTTP_201_CREATED
)
async def add_item_to_cart(
    payload: CartItemCreate,
    current_user: UserModel = Depends(get_current_user),
    service: CartService = Depends(get_cart_service),
):
    return await service.add_item(current_user.id, payload)


@items_router.put("/{product_id}", response_model=CartItemSchema)
async def update_cart_item(
    product_id: int,
    payload: CartItemUpdate,
    current_user: UserModel = Depends(get_current_user),
    service: CartService = Depends(get_cart_service),
):
    return await service.update_item(current_user.id, product_id, payload)


@items_router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_cart_item(
    product_id: int,
    current_user: UserModel = Depends(get_current_user),
    service: CartService = Depends(get_cart_service),
):
    await service.remove_item(current_user.id, product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    current_user: UserModel = Depends(get_current_user),
    service: CartService = Depends(get_cart_service),
):
    await service.clear(current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


router.include_router(items_router)
