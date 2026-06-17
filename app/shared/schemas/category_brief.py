from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class CategoryBrief(BaseModel):
    id: Annotated[int, Field(description="ID категории")]
    name: Annotated[str, Field(description="Название категории")]

    model_config = ConfigDict(from_attributes=True)
