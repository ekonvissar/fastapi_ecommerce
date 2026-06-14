from datetime import datetime, timedelta, timezone
from typing import Literal, TypedDict
from uuid import uuid4

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, SettingsDep
from app.db.deps import get_async_db
from app.models.users import User as UserModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")
Role = Literal["buyer", "seller", "admin"]


class TokenUserData(TypedDict):
    sub: str
    role: Role
    id: int


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: TokenUserData, settings: Settings) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "token_type": "access", "jti": str(uuid4())})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.algorithm)


def create_refresh_token(data: TokenUserData, settings: Settings) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "token_type": "refresh", "jti": str(uuid4())})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.algorithm)


async def get_current_user(
    settings: SettingsDep,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.algorithm]
        )
        email: str = payload.get("sub")
        token_type: str = payload.get("token_type")

        if email is None or token_type != "access":
            raise credentials_exception

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise credentials_exception

    result = await db.scalars(
        select(UserModel).where(UserModel.email == email, UserModel.is_active)
    )
    user = result.first()
    if user is None:
        raise credentials_exception
    return user


def required_role(role: Role):
    async def dep(current_user: UserModel = Depends(get_current_user)) -> UserModel:
        if current_user.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Only {role}s can perform this action",
            )
        return current_user

    return dep


get_current_seller = required_role("seller")
get_current_buyer = required_role("buyer")
get_current_admin = required_role("admin")
