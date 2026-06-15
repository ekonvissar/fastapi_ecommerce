"""Обратная совместимость: остальной код импортирует из app.auth."""

from app.identity.deps import (
    get_current_admin,
    get_current_buyer,
    get_current_seller,
    get_current_user,
    oauth2_scheme,
)
from app.identity.services.token_service import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    Role,
    TokenUserData,
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)

__all__ = [
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    "REFRESH_TOKEN_EXPIRE_DAYS",
    "Role",
    "TokenUserData",
    "create_access_token",
    "create_refresh_token",
    "get_current_admin",
    "get_current_buyer",
    "get_current_seller",
    "get_current_user",
    "hash_password",
    "oauth2_scheme",
    "verify_password",
]
