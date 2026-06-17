from app.identity.exceptions import EmailAlreadyExistsError
from app.identity.repositories.user_repository import UserRepository
from app.identity.schemas.user import UserCreate
from app.identity.services.token_service import hash_password
from app.models.users import User as UserModel


class UserService:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    async def register(self, data: UserCreate) -> UserModel:
        existing = await self._users.get_by_email(data.email)
        if existing:
            raise EmailAlreadyExistsError

        user = UserModel(
            email=data.email,
            hashed_password=hash_password(data.password),
            role=data.role,
        )
        await self._users.add(user)
        await self._users.commit()
        return user
