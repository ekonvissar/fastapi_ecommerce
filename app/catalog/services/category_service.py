from app.catalog.exceptions import (
    CategoryNotFoundError,
    CategorySelfParentError,
    ParentCategoryNotFoundError,
)
from app.catalog.repositories.category_repository import CategoryRepository
from app.catalog.schemas.category import CategoryCreate
from app.models.categories import Category as CategoryModel


class CategoryService:
    def __init__(self, categories: CategoryRepository) -> None:
        self._categories = categories

    async def list_categories(self) -> list[CategoryModel]:
        return await self._categories.list_active()

    async def _validate_parent(self, parent_id: int | None) -> None:
        if parent_id is None:
            return
        parent = await self._categories.get_active_by_id(parent_id)
        if parent is None:
            raise ParentCategoryNotFoundError

    async def create(self, data: CategoryCreate) -> CategoryModel:
        await self._validate_parent(data.parent_id)
        category = CategoryModel(**data.model_dump())
        await self._categories.add(category)
        await self._categories.commit()
        loaded = await self._categories.get_with_parent(category.id)
        return loaded or category

    async def update(self, category_id: int, data: CategoryCreate) -> CategoryModel:
        category = await self._categories.get_active_by_id(category_id)
        if category is None:
            raise CategoryNotFoundError

        if data.parent_id is not None:
            parent = await self._categories.get_active_by_id(data.parent_id)
            if parent is None:
                raise ParentCategoryNotFoundError
            if parent.id == category_id:
                raise CategorySelfParentError

        update_data = data.model_dump(exclude_unset=True)
        await self._categories.update_fields(category_id, update_data)
        await self._categories.commit()
        loaded = await self._categories.get_with_parent(category_id)
        return loaded or category

    async def delete(self, category_id: int) -> CategoryModel:
        category = await self._categories.get_active_by_id(category_id)
        if category is None:
            raise CategoryNotFoundError

        await self._categories.soft_delete(category_id)
        await self._categories.commit()
        return category
