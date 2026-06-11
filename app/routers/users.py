from datetime import datetime, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import (
    REFRESH_TOKEN_EXPIRE_DAYS,
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.config import SettingsDep
from app.db_depends import get_async_db, get_redis
from app.models.users import User as UserModel
from app.schemas import User as UsersSchema
from app.schemas import UserCreate

router = APIRouter(prefix="/users", tags=["users"])


COOKIE_MAX_AGE = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60


@router.post("/", response_model=UsersSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_async_db)):
    result = await db.scalar(select(UserModel).where(UserModel.email == user.email))
    if result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already exists"
        )

    db_user = UserModel(
        email=user.email, hashed_password=hash_password(user.password), role=user.role
    )

    db.add(db_user)
    await db.commit()
    return db_user


@router.post("/token")
async def login(
    response: Response,
    settings: SettingsDep,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db),
    redis: Redis = Depends(get_redis),
):
    user = await db.scalar(
        select(UserModel).where(
            UserModel.email == form_data.username, UserModel.is_active
        )
    )

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "id": user.id},
        settings=settings,
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email, "role": user.role, "id": user.id},
        settings=settings,
    )

    refresh_payload = jwt.decode(
        refresh_token,
        settings.jwt_secret,
        algorithms=[settings.algorithm],
        options={"verify_exp": False},
    )
    jti = refresh_payload["jti"]

    # Сохраняем jti в Redis — whitelist
    # Ключ: refresh:{user_id}:{jti}, значение: user_id, TTL = срок жизни токена
    await redis.set(
        f"refresh:{user.id}:{jti}",
        str(user.id),
        ex=COOKIE_MAX_AGE,
    )

    # Все атрибуты куки одинаковые везде — иначе браузер считает их разными куками
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,  # недоступна из JS — защита от XSS
        secure=True,  # только HTTPS
        samesite="lax",  # защита от CSRF, но позволяет переходы по ссылкам
        max_age=COOKIE_MAX_AGE,
        path="/users",  # кука отправляется только на /users/*
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/refresh")
async def refresh(
    request: Request,
    response: Response,
    settings: SettingsDep,
    db: AsyncSession = Depends(get_async_db),
    redis: Redis = Depends(get_redis),
):
    refresh_cookie = request.cookies.get("refresh_token")
    if not refresh_cookie:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token"
        )

    try:
        payload = jwt.decode(
            refresh_cookie, settings.jwt_secret, algorithms=[settings.algorithm]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    # Исправленная проверка типа токена (был баг — "refresh_token" вместо "token_type")
    if payload.get("token_type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong token type"
        )

    jti = payload.get("jti")
    user_id = payload.get("id")
    key = f"refresh:{user_id}:{jti}"

    # Атомарно удаляем jti из Redis
    # Если токен уже использован или не существует — возможна кража
    deleted = await redis.delete(key)
    if not deleted:
        # Токен не найден в whitelist — либо уже использован, либо украден
        # Удаляем все сессии пользователя на всякий случай
        async for k in redis.scan_iter(f"refresh:{user_id}:*"):
            await redis.delete(k)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token reuse detected"
        )

    # Проверяем что пользователь существует и активен в БД
    user = await db.scalar(
        select(UserModel).where(
            UserModel.id == user_id,
            UserModel.is_active,
        )
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Выпускаем новый access-токен
    new_access_token = create_access_token(
        {"sub": user.email, "role": user.role, "id": user.id},
        settings=settings,
    )

    # Ротация refresh-токена — всегда выпускаем новый
    new_refresh_token = create_refresh_token(
        {"sub": user.email, "role": user.role, "id": user.id},
        settings=settings,
    )

    # Достаём jti нового refresh-токена и сохраняем в Redis
    new_payload = jwt.decode(
        new_refresh_token,
        settings.jwt_secret,
        algorithms=[settings.algorithm],
        options={"verify_exp": False},
    )
    new_jti = new_payload["jti"]

    # Исправлен баг с naive/aware datetime — используем fromtimestamp с tz=UTC
    exp = datetime.fromtimestamp(new_payload["exp"], tz=timezone.utc)
    now = datetime.now(timezone.utc)
    ttl = int((exp - now).total_seconds())

    await redis.set(
        f"refresh:{user.id}:{new_jti}",
        str(user.id),
        ex=ttl,
    )

    # Те же атрибуты куки что и при логине
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=COOKIE_MAX_AGE,
        path="/users",
    )

    return {"access_token": new_access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    settings: SettingsDep,
    redis: Redis = Depends(get_redis),
):
    refresh_cookie = request.cookies.get("refresh_token")

    if refresh_cookie:
        try:
            payload = jwt.decode(
                refresh_cookie,
                settings.jwt_secret,
                algorithms=[settings.algorithm],
                options={"verify_exp": False},  # при логауте срок не важен
            )
            jti = payload.get("jti")
            user_id = payload.get("id")

            # Удаляем refresh-токен из whitelist
            await redis.delete(f"refresh:{user_id}:{jti}")

        except jwt.PyJWTError:
            pass  # токен повреждён — просто удаляем куку

    # Удаляем куку — те же атрибуты что при установке
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="lax",
        path="/users",
    )

    return {"detail": "Logged out"}
