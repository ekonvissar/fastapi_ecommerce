from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.identity.deps import get_auth_service, get_user_service
from app.identity.schemas.user import User as UserSchema
from app.identity.schemas.user import UserCreate
from app.identity.services.auth_service import AuthService
from app.identity.services.token_service import REFRESH_COOKIE_MAX_AGE
from app.identity.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

REFRESH_COOKIE_PATH = "/users"


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=REFRESH_COOKIE_MAX_AGE,
        path=REFRESH_COOKIE_PATH,
    )


def _delete_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="lax",
        path=REFRESH_COOKIE_PATH,
    )


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    service: UserService = Depends(get_user_service),
):
    return await service.register(user)


@router.post("/token")
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):
    tokens = await service.login(form_data.username, form_data.password)
    _set_refresh_cookie(response, tokens.refresh_token)
    return {"access_token": tokens.access_token, "token_type": "bearer"}


@router.post("/refresh")
async def refresh(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    tokens = await service.refresh(request.cookies.get("refresh_token"))
    _set_refresh_cookie(response, tokens.refresh_token)
    return {"access_token": tokens.access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    await service.logout(request.cookies.get("refresh_token"))
    _delete_refresh_cookie(response)
    return {"detail": "Logged out"}
