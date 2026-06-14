from datetime import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import Form
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CategoryBrief(BaseModel):
    id: Annotated[int, Field(description="ID категории")]
    name: Annotated[str, Field(description="Название категории")]

    model_config = ConfigDict(from_attributes=True)


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


class ProductSnapshot(BaseModel):
    id: Annotated[int, Field(description="ID товара")]
    name: Annotated[str, Field(description="Название товара на момент заказа")]
    image_url: Annotated[str | None, Field(None, description="URL изображения")]

    model_config = ConfigDict(from_attributes=True)


class ProductBrief(BaseModel):
    id: Annotated[int, Field(description="ID товара")]
    name: Annotated[str, Field(description="Название товара")]

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: Annotated[EmailStr, Field(description="Email пользователя")]
    password: Annotated[
        str, Field(min_length=8, description="Пароль (минимум 8 символов)")
    ]
    role: Annotated[
        str,
        Field(
            default="buyer",
            pattern="^(buyer|seller|admin)$",
            description="Роль: 'buyer', 'seller' или 'admin'",
        ),
    ]


class User(BaseModel):
    id: Annotated[int, Field(description="Уникальный идентификатор пользователя")]
    email: Annotated[EmailStr, Field(description="Логин или почта")]
    is_active: Annotated[bool, Field(description="Активность пользователя")]
    role: Annotated[str, Field(description="Роль пользователя")]

    model_config = ConfigDict(from_attributes=True)


class UserPublic(BaseModel):
    id: Annotated[int, Field(description="ID пользователя")]
    email: Annotated[EmailStr, Field(description="Email пользователя")]

    model_config = ConfigDict(from_attributes=True)


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


class RefreshTokenRequest(BaseModel):
    refresh_token: str


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


class PaginationResponse[T](BaseModel):
    items: list[T] = Field(..., description="Элементы текущей страницы")
    total: int = Field(ge=0, description="Общее количество")
    page: int = Field(ge=1, description="Текущая страница")
    page_size: int = Field(ge=1, description="Размер страницы")


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


type ProductList = PaginationResponse[Product]
type OrderList = PaginationResponse[Order]
