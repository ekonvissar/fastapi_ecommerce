from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class ProductBrief(BaseModel):
    id: Annotated[int, Field(description="ID товара")]
    name: Annotated[str, Field(description="Название товара")]

    model_config = ConfigDict(from_attributes=True)


class ProductSnapshot(BaseModel):
    id: Annotated[int, Field(description="ID товара")]
    name: Annotated[str, Field(description="Название товара на момент заказа")]
    image_url: Annotated[str | None, Field(None, description="URL изображения")]

    model_config = ConfigDict(from_attributes=True)
