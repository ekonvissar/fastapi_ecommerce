from pydantic import BaseModel, Field


class PaginationResponse[T](BaseModel):
    items: list[T] = Field(..., description="Элементы текущей страницы")
    total: int = Field(ge=0, description="Общее количество")
    page: int = Field(ge=1, description="Текущая страница")
    page_size: int = Field(ge=1, description="Размер страницы")
