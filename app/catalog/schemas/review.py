from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.identity.schemas.user import UserPublic
from app.shared.schemas.product_brief import ProductBrief


class ReviewCreate(BaseModel):
    product_id: Annotated[int, Field(description="Уникальный идентификатор товара")]
    comment: Annotated[
        str | None,
        Field(
            None,
            min_length=1,
            max_length=1000,
            description="Отзыв (длина от 1 до 1000 символов)",
        ),
    ]
    grade: Annotated[
        int, Field(ge=1, le=5, description="Рейтнг пользователя от 1 до 5")
    ]


class Review(BaseModel):
    id: Annotated[int, Field(description="Уникальный идентификатор отзыва")]
    user_id: Annotated[
        int,
        Field(description="Уникальный идентификатор пользователя, оставивший отзыв"),
    ]
    product_id: Annotated[
        int,
        Field(
            description="Уникальный идентификатор продукта, на который оставляют отзыв"
        ),
    ]
    comment: Annotated[
        str | None, Field(None, description="Отзыв пользователя на товар")
    ]
    comment_date: Annotated[datetime, Field(description="Дата оставления отзыва")]
    grade: Annotated[int, Field(description="Оценка паользователя от 1 до 5")]
    is_active: Annotated[bool, Field(description="Активность отзыва")]
    user: Annotated[UserPublic | None, Field(None, description="Автор отзыва")]
    product: Annotated[
        ProductBrief | None,
        Field(None, description="Товар, к которому относится отзыв"),
    ]

    model_config = ConfigDict(from_attributes=True)
