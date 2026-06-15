from dataclasses import dataclass

import jwt

from app.config import Settings
from app.identity.exceptions import (
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    MissingRefreshTokenError,
    RefreshTokenExpiredError,
    TokenReuseDetectedError,
    UserInactiveOrNotFoundError,
    WrongTokenTypeError,
)
from app.identity.repositories.refresh_token_store import RefreshTokenStore
from app.identity.repositories.user_repository import UserRepository
from app.identity.services.token_service import (
    REFRESH_COOKIE_MAX_AGE,
    create_access_token,
    create_refresh_token,
    decode_token,
    refresh_ttl_seconds,
    token_user_data,
    verify_password,
)


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str


class AuthService:
    def __init__(
        self,
        users: UserRepository,
        refresh_store: RefreshTokenStore,
        settings: Settings,
    ) -> None:
        self._users = users
        self._refresh_store = refresh_store
        self._settings = settings

    async def login(self, email: str, password: str) -> TokenPair:
        user = await self._users.get_active_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError

        return await self._issue_token_pair(user)

    async def refresh(self, refresh_token: str | None) -> TokenPair:
        if not refresh_token:
            raise MissingRefreshTokenError

        try:
            payload = decode_token(refresh_token, self._settings)
        except jwt.ExpiredSignatureError:
            raise RefreshTokenExpiredError from None
        except jwt.InvalidTokenError:
            raise InvalidRefreshTokenError from None

        if payload.get("token_type") != "refresh":
            raise WrongTokenTypeError

        jti = payload.get("jti")
        user_id = payload.get("id")
        if not jti or not user_id:
            raise InvalidRefreshTokenError

        deleted = await self._refresh_store.delete(user_id, jti)
        if not deleted:
            await self._refresh_store.delete_all_for_user(user_id)
            raise TokenReuseDetectedError

        user = await self._users.get_active_by_id(user_id)
        if not user:
            raise UserInactiveOrNotFoundError

        return await self._issue_token_pair(
            user, refresh_ttl=refresh_ttl_seconds(payload)
        )

    async def logout(self, refresh_token: str | None) -> None:
        if not refresh_token:
            return

        try:
            payload = decode_token(refresh_token, self._settings, verify_exp=False)
            jti = payload.get("jti")
            user_id = payload.get("id")
            if jti and user_id:
                await self._refresh_store.delete(user_id, jti)
        except jwt.PyJWTError:
            pass

    async def _issue_token_pair(
        self, user, *, refresh_ttl: int | None = None
    ) -> TokenPair:
        user_data = token_user_data(user)
        access_token = create_access_token(user_data, self._settings)
        refresh_token = create_refresh_token(user_data, self._settings)

        payload = decode_token(refresh_token, self._settings, verify_exp=False)
        ttl = refresh_ttl if refresh_ttl is not None else REFRESH_COOKIE_MAX_AGE
        await self._refresh_store.save(user.id, payload["jti"], ttl)

        return TokenPair(access_token=access_token, refresh_token=refresh_token)
