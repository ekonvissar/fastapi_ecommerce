from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, EmailStr
from decimal import Decimal
from typing import Annotated

class CategoryCreate(BaseModel):
    """
    Модель для создания и обновления категории.
    Используется в POST и PUT запросах.
    """
    name: Annotated[str,  Field(min_length=3, max_length=50, description="Название категории (3-50 символов)")]
    parent_id: Annotated[int | None,  Field(None, description='ID родительской категории, если есть')]

class Category(BaseModel):
    """
    Модель для ответа с данными категории.
    Используется в GET-запросах.
    """
    id: Annotated[int,  Field(description='Уникальный идентификатор категории')]
    name: Annotated[str, Field(description='Название категории')]
    parent_id: Annotated[int | None, Field(None, description="ID родительской категории, если есть")]
    is_active: Annotated[bool, Field(description="Активность категории")]

model_config = ConfigDict(from_attributes=True)

class ProductCreate(BaseModel):
    """
    Модель для создания и обновления товара.
    Используется в POST и PUT запросах.
    """
    name: Annotated[str,  Field(min_length=3, max_length=100,
                      description="Название товара (3-100 символов)")]
    description: Annotated[str | None, Field(None, max_length=500,
                                             description="Описание товара (до 500 символов)")]
    price: Annotated[Decimal, Field(gt=0, description="Цена товара (больше 0)", decimal_places=2)]
    image_url: Annotated[str | None, Field(None, max_length=200, description="URL изображения товара")]
    stock: Annotated[int,  Field(ge=0, description="Количество товара на складе (0 или больше)")]
    category_id: Annotated[int,  Field(description="ID категории, к которой относится товар")]
    rating: Annotated[float, Field(ge=1, le=5, description="Рейтинг продукта")]


class Product(BaseModel):
    """
    Модель для ответа с данными товара.
    Используется в GET-запросах.
    """
    id: Annotated[int,  Field(description="Уникальный идентификатор товара")]
    name: Annotated[str,  Field(description="Название товара")]
    description: Annotated[str | None, Field(None, description="Описание товара")]
    price: Annotated[Decimal, Field(description="Цена товара в рублях", gt=0, decimal_places=2)]
    image_url: Annotated[str | None, Field(None, description="URL изображения товара")]
    stock: Annotated[int,  Field(description="Количество товара на складе")]
    rating: Annotated[float, Field(description="Рейтинг продукта")]
    category_id: Annotated[int,  Field(description="ID категории")]
    is_active: Annotated[bool, Field(description="Активность товара")]

    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    email: Annotated[EmailStr, Field(description="Email пользователя")]
    password: Annotated[str, Field(min_length=8, description="Пароль (минимум 8 символов)")]
    role: Annotated[str, Field(default="buyer", pattern="^(buyer|seller|admin)$", description="Роль: 'buyer', 'seller' или 'admin'")]

class User(BaseModel):
    id: Annotated[int, Field(description="Уникальный идентификатор пользователя")]
    email: Annotated[EmailStr, Field(description="Логин или почта")]
    is_active: Annotated[bool, Field(description="Активность пользователя")]
    role: Annotated[str, Field(description="Роль пользователя")]

    model_config = ConfigDict(from_attributes=True)

class ReviewCreate(BaseModel):
    product_id: Annotated[int, Field(description="Уникальный идентификатор товара")]
    comment: Annotated[str | None, Field(None, min_length=1, max_length=1000, description="Отзыв (длина от 1 до 1000 символов)")]
    grade: Annotated[int, Field(ge=1, le=5, description="Рейтнг пользователя от 1 до 5")]

class Review(BaseModel):
    id: Annotated[int, Field(description="Уникальный идентификатор отзыва")]
    user_id: Annotated[int, Field(description="Уникальный идентификатор пользователя, оставивший отзыв")]
    product_id: Annotated[int, Field(description="Уникальный идентификатор продукта, на который оставляют отзыв")]
    comment: Annotated[str | None, Field(None, description="Отзыв пользователя на товар")]
    comment_date: Annotated[datetime, Field(description="Дата оставления отзыва")]
    grade: Annotated[int, Field(description="Оценка паользователя от 1 до 5")]
    is_active: Annotated[bool, Field(description="Активность отзыва")]

    model_config = ConfigDict(from_attributes=True)

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ProductList(BaseModel):
    items: Annotated[list[Product], Field(description="Товары для текущей страницы")]
    total: Annotated[int, Field(ge=0, description="Общее количество товаров")]
    page: Annotated[int, Field(ge=1, description="Номер текущей страницы")]
    page_size: Annotated[int, Field(ge=1, description="Количество элементов на странице")]

    model_config = ConfigDict(from_attributes=True)  # Для чтения из ORM-объектов