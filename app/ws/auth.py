import jwt
from fastapi import HTTPException, status

from app.config import Settings


def get_user_id_from_token(token: str, settings: Settings) -> int:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.algorithm]
        )
        user_id = payload.get("id")
        token_type = payload.get("token_type")

        if user_id is None or token_type != "access":
            raise credentials_exception

        return int(user_id)
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        ) from exc
    except jwt.PyJWTError as exc:
        raise credentials_exception from exc
