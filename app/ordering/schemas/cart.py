from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.shared.schemas.product import Product


class CartItemBase(BaseModel):
    product_id: Annotated[int, Field(description="ID товара")]
    quantity: Annotated[int, Field(ge=1, description="Количество товара")]


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: Annotated[int, Field(..., ge=1, description="Новое количество товара")]


class CartItem(BaseModel):
    id: Annotated[int, Field(..., description="ID позиции корзины")]
    quantity: Annotated[int, Field(..., ge=1, description="Количество товара")]
    product: Annotated[Product, Field(..., description="Информация о товаре")]

    model_config = ConfigDict(from_attributes=True)


class Cart(BaseModel):
    user_id: Annotated[int, Field(..., description="ID пользователя")]
    items: Annotated[
        list[CartItem], Field(default_factory=list, description="Содержимое корзины")
    ]
    total_quantity: Annotated[
        int, Field(..., ge=0, description="Общее количество товаров")
    ]
    total_price: Annotated[
        Decimal, Field(..., ge=0, description="Общая стоимость товаров")
    ]

    model_config = ConfigDict(from_attributes=True)
