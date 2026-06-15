from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.shared.schemas.category_brief import CategoryBrief


class Product(BaseModel):
    id: Annotated[int, Field(description="Уникальный идентификатор товара")]
    name: Annotated[str, Field(description="Название товара")]
    description: Annotated[str | None, Field(None, description="Описание товара")]
    price: Annotated[
        Decimal, Field(description="Цена товара в рублях", gt=0, decimal_places=2)
    ]
    image_url: Annotated[str | None, Field(None, description="URL изображения товара")]
    stock: Annotated[int, Field(description="Количество товара на складе")]
    rating: Annotated[float, Field(description="Рейтинг продукта")]
    category_id: Annotated[int, Field(description="ID категории")]
    category: Annotated[
        CategoryBrief | None, Field(None, description="Категория товара")
    ]
    is_active: Annotated[bool, Field(description="Активность товара")]

    model_config = ConfigDict(from_attributes=True)
