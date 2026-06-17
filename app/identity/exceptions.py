from fastapi import status


class IdentityError(Exception):
    """Ошибка аутентификации/регистрации с HTTP-маппингом."""

    def __init__(
        self,
        detail: str,
        *,
        status_code: int = status.HTTP_401_UNAUTHORIZED,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.detail = detail
        self.status_code = status_code
        self.headers = headers or {}


class EmailAlreadyExistsError(IdentityError):
    def __init__(self) -> None:
        super().__init__(
            "Email already exists",
            status_code=status.HTTP_409_CONFLICT,
        )


class InvalidCredentialsError(IdentityError):
    def __init__(self) -> None:
        super().__init__(
            "Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


class MissingRefreshTokenError(IdentityError):
    def __init__(self) -> None:
        super().__init__("Missing refresh token")


class RefreshTokenExpiredError(IdentityError):
    def __init__(self) -> None:
        super().__init__("Refresh token is expired")


class InvalidRefreshTokenError(IdentityError):
    def __init__(self) -> None:
        super().__init__("Invalid refresh token")


class WrongTokenTypeError(IdentityError):
    def __init__(self) -> None:
        super().__init__("Wrong token type")


class TokenReuseDetectedError(IdentityError):
    def __init__(self) -> None:
        super().__init__("Token reuse detected")


class UserInactiveOrNotFoundError(IdentityError):
    def __init__(self) -> None:
        super().__init__("User not found or inactive")
