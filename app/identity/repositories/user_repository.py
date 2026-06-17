from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User as UserModel


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_email(self, email: str) -> UserModel | None:
        return await self._db.scalar(select(UserModel).where(UserModel.email == email))

    async def get_active_by_email(self, email: str) -> UserModel | None:
        return await self._db.scalar(
            select(UserModel).where(UserModel.email == email, UserModel.is_active)
        )

    async def get_active_by_id(self, user_id: int) -> UserModel | None:
        return await self._db.scalar(
            select(UserModel).where(UserModel.id == user_id, UserModel.is_active)
        )

    async def add(self, user: UserModel) -> None:
        self._db.add(user)

    async def commit(self) -> None:
        await self._db.commit()
