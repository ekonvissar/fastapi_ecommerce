from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.categories import Category as CategoryModel

_CATEGORY_WITH_PARENT = (selectinload(CategoryModel.parent),)


class CategoryRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_active(self) -> list[CategoryModel]:
        result = await self._db.scalars(
            select(CategoryModel)
            .options(*_CATEGORY_WITH_PARENT)
            .where(CategoryModel.is_active)
        )
        return list(result.all())

    async def get_active_by_id(self, category_id: int) -> CategoryModel | None:
        result = await self._db.scalars(
            select(CategoryModel)
            .options(*_CATEGORY_WITH_PARENT)
            .where(CategoryModel.id == category_id, CategoryModel.is_active)
        )
        return result.first()

    async def get_by_id(self, category_id: int) -> CategoryModel | None:
        result = await self._db.scalars(
            select(CategoryModel)
            .options(*_CATEGORY_WITH_PARENT)
            .where(CategoryModel.id == category_id)
        )
        return result.first()

    async def get_with_parent(self, category_id: int) -> CategoryModel | None:
        return await self.get_by_id(category_id)

    async def add(self, category: CategoryModel) -> None:
        self._db.add(category)

    async def update_fields(self, category_id: int, data: dict) -> None:
        await self._db.execute(
            update(CategoryModel).where(CategoryModel.id == category_id).values(**data)
        )

    async def soft_delete(self, category_id: int) -> None:
        await self._db.execute(
            update(CategoryModel)
            .where(CategoryModel.id == category_id)
            .values(is_active=False)
        )

    async def commit(self) -> None:
        await self._db.commit()
