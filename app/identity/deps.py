import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import SettingsDep
from app.db.deps import get_async_db, get_redis
from app.identity.repositories.refresh_token_store import RefreshTokenStore
from app.identity.repositories.user_repository import UserRepository
from app.identity.services.auth_service import AuthService
from app.identity.services.token_service import decode_token
from app.identity.services.user_service import UserService
from app.models.users import User as UserModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")


def get_user_repository(
    db: AsyncSession = Depends(get_async_db),
) -> UserRepository:
    return UserRepository(db)


def get_refresh_token_store(redis=Depends(get_redis)) -> RefreshTokenStore:
    return RefreshTokenStore(redis)


def get_user_service(
    users: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(users)


def get_auth_service(
    settings: SettingsDep,
    users: UserRepository = Depends(get_user_repository),
    refresh_store: RefreshTokenStore = Depends(get_refresh_token_store),
) -> AuthService:
    return AuthService(users, refresh_store, settings)


async def get_current_user(
    settings: SettingsDep,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db),
) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token, settings)
        email: str = payload.get("sub")
        token_type: str = payload.get("token_type")

        if email is None or token_type != "access":
            raise credentials_exception

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
    except jwt.PyJWTError:
        raise credentials_exception

    users = UserRepository(db)
    user = await users.get_active_by_email(email)
    if user is None:
        raise credentials_exception
    return user


def required_role(role: str):
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
