from datetime import datetime, timedelta, timezone
from typing import Literal, TypedDict
from uuid import uuid4

import jwt
from passlib.context import CryptContext

from app.config import Settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
REFRESH_COOKIE_MAX_AGE = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

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


def decode_token(token: str, settings: Settings, *, verify_exp: bool = True) -> dict:
    options = {"verify_exp": verify_exp}
    return jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.algorithm],
        options=options,
    )


def token_user_data(user) -> TokenUserData:
    return {"sub": user.email, "role": user.role, "id": user.id}


def refresh_ttl_seconds(payload: dict) -> int:
    exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    now = datetime.now(timezone.utc)
    return int((exp - now).total_seconds())
