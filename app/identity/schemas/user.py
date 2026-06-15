from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field


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
