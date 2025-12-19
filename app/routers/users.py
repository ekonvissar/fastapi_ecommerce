from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm
import jwt
from datetime import datetime, timedelta, timezone

from app.models.users import User as UserModel
from app.schemas import UserCreate, User as UsersSchema, RefreshTokenRequest
from app.db_depends import get_async_db
from app.auth import hash_password, verify_password, create_access_token, create_refresh_token, \
    REFRESH_TOKEN_EXPIRE_DAYS
from app.config import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UsersSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_async_db)):
    result = await db.scalar(select(UserModel).where(UserModel.email == user.email))
    if result:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    db_user = UserModel(
        email=user.email,
        hashed_password=hash_password(user.password),
        role=user.role
    )

    db.add(db_user)
    await db.commit()
    return db_user


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                db: AsyncSession = Depends(get_async_db),
                response: Response = None):
    user = await db.scalar(select(UserModel).where(UserModel.email == form_data.username,
                                                   UserModel.is_active == True))

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect email or password",
                            headers={"WWW-Authenticate": "Bearer"})

    access_token = create_access_token(data={"sub": user.email,
                                             "role": user.role,
                                             "id": user.id})
    refresh_token = create_refresh_token(data={"sub": user.email,
                                               "role": user.role,
                                               "id": user.id})

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS,
        path="/users/refresh"
    )

    return {"access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"}


@router.post("/refresh")
async def refresh(request: Request, response: Response):
    refresh_cookie = request.cookies.get("refresh_token")
    if not refresh_cookie:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Missing refresh token")

    try:
        payload = jwt.decode(refresh_cookie, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Refresh token is expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid refresh token")

    if payload.get("refresh_token") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Wrong token type")

    new_access_token = create_access_token({
        "sub": payload["sub"],
        "role": payload["role"],
        "id": payload["id"]
    })

    exp = datetime.fromtimestamp(payload["exp"])
    now = datetime.now(timezone.utc)
    if exp - now < timedelta(days=1):
        new_refresh_token = create_refresh_token({
            "sub": payload["sub"],
            "role": payload["role"],
            "id": payload["id"]
        })

        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=REFRESH_TOKEN_EXPIRE_DAYS,
            path="/"
        )

    return {"access_token": new_access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="refresh_token",
                           httponly=True,
                           secure=True,
                           samesite="strict",
                           path="/")

    return {"detail": "Logged out"}