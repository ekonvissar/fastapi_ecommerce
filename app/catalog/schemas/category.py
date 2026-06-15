from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.shared.schemas.category_brief import CategoryBrief


class CategoryCreate(BaseModel):
    name: Annotated[
        str,
        Field(
            min_length=3,
            max_length=50,
            description="Название категории (3-50 символов)",
        ),
    ]
    parent_id: Annotated[
        int | None, Field(None, description="ID родительской категории, если есть")
    ]


class Category(BaseModel):
    id: Annotated[int, Field(description="Уникальный идентификатор категории")]
    name: Annotated[str, Field(description="Название категории")]
    parent_id: Annotated[
        int | None, Field(None, description="ID родительской категории, если есть")
    ]
    is_active: Annotated[bool, Field(description="Активность категории")]
    parent: Annotated[
        CategoryBrief | None, Field(None, description="Родительская категория")
    ]

    model_config = ConfigDict(from_attributes=True)
