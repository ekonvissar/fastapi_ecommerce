from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.identity.schemas.user import UserPublic
from app.shared.schemas.pagination import PaginationResponse
from app.shared.schemas.product_brief import ProductSnapshot


class OrderItem(BaseModel):
    id: int = Field(..., description="ID позиции заказа")
    product_id: int = Field(..., description="ID товара")
    quantity: int = Field(..., ge=1, description="Количество")
    unit_price: Decimal = Field(
        ..., ge=0, description="Цена за единицу на момент покупки"
    )
    total_price: Decimal = Field(..., ge=0, description="Сумма по позиции")
    product: ProductSnapshot = Field(..., description="Снимок товара на момент заказа")

    model_config = ConfigDict(from_attributes=True)


class Order(BaseModel):
    id: int = Field(..., description="ID заказа")
    user_id: int = Field(..., description="ID пользователя")
    user: UserPublic | None = Field(None, description="Покупатель для админ-эндпоинтов")
    status: str = Field(..., description="Текущий статус заказа")
    total_amount: Decimal = Field(..., ge=0, description="Общая стоимость")
    created_at: datetime = Field(..., description="Когда заказ был создан")
    updated_at: datetime = Field(..., description="Когда последний раз обновлялся")
    items: list[OrderItem] = Field(default_factory=list, description="Список позиций")

    model_config = ConfigDict(from_attributes=True)


type OrderList = PaginationResponse[Order]
