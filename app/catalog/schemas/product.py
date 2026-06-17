from decimal import Decimal
from typing import Annotated

from fastapi import Form
from pydantic import BaseModel, Field

from app.shared.schemas.pagination import PaginationResponse
from app.shared.schemas.product import Product


class ProductCreate(BaseModel):
    name: Annotated[
        str,
        Field(
            ...,
            min_length=3,
            max_length=100,
            description="Название товара (3-100 символов)",
        ),
    ]
    description: Annotated[
        str | None,
        Field(None, max_length=500, description="Описание товара (до 500 символов)"),
    ]
    price: Decimal = Field(gt=0, description="Цена товара (больше 0)", decimal_places=2)
    stock: Annotated[
        int, Field(..., ge=0, description="Количество товара на складе (0 или больше)")
    ]
    category_id: Annotated[
        int, Field(..., description="ID категории, к которой относится товар")
    ]

    @classmethod
    def as_form(
        cls,
        name: Annotated[str, Form(...)],
        price: Annotated[Decimal, Form(...)],
        stock: Annotated[int, Form(...)],
        category_id: Annotated[int, Form(...)],
        description: Annotated[str | None, Form()] = None,
    ) -> "ProductCreate":
        return cls(
            name=name,
            description=description,
            price=price,
            stock=stock,
            category_id=category_id,
        )


type ProductList = PaginationResponse[Product]
