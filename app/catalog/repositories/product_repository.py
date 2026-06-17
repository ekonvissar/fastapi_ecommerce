from dataclasses import dataclass

from sqlalchemy import desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.products import Product as ProductModel

_PRODUCT_WITH_CATEGORY = (selectinload(ProductModel.category),)


@dataclass
class ProductListFilters:
    page: int
    page_size: int
    category_id: int | None = None
    search: str | None = None
    min_price: float | None = None
    max_price: float | None = None
    in_stock: bool | None = None
    seller_id: int | None = None


class ProductRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    def _build_filters(self, filters: ProductListFilters) -> list:
        conditions = [ProductModel.is_active.is_(True)]
        if filters.category_id is not None:
            conditions.append(ProductModel.category_id == filters.category_id)
        if filters.min_price is not None:
            conditions.append(ProductModel.price >= filters.min_price)
        if filters.max_price is not None:
            conditions.append(ProductModel.price <= filters.max_price)
        if filters.in_stock is not None:
            conditions.append(
                ProductModel.stock > 0 if filters.in_stock else ProductModel.stock == 0
            )
        if filters.seller_id is not None:
            conditions.append(ProductModel.seller_id == filters.seller_id)
        return conditions

    async def list_filtered(self, filters: ProductListFilters) -> tuple[list, int]:
        conditions = self._build_filters(filters)
        rank_col = None

        if filters.search:
            search_value = filters.search.strip()
            if search_value:
                ts_query = func.websearch_to_tsquery("english", search_value)
                conditions.append(ProductModel.tsv.op("@@")(ts_query))
                rank_col = func.ts_rank_cd(ProductModel.tsv, ts_query).label("rank")

        total_stmt = select(func.count()).select_from(ProductModel).where(*conditions)
        total = await self._db.scalar(total_stmt) or 0

        if rank_col is not None:
            stmt = (
                select(ProductModel, rank_col)
                .where(*conditions)
                .order_by(desc(rank_col), ProductModel.id)
                .offset((filters.page - 1) * filters.page_size)
                .limit(filters.page_size)
            )
            result = await self._db.execute(stmt)
            items = [row[0] for row in result.all()]
        else:
            stmt = (
                select(ProductModel)
                .options(*_PRODUCT_WITH_CATEGORY)
                .where(*conditions)
                .order_by(ProductModel.id)
                .offset((filters.page - 1) * filters.page_size)
                .limit(filters.page_size)
            )
            items = list((await self._db.scalars(stmt)).all())

        return items, total

    async def list_by_category(self, category_id: int) -> list[ProductModel]:
        result = await self._db.scalars(
            select(ProductModel)
            .options(*_PRODUCT_WITH_CATEGORY)
            .where(ProductModel.category_id == category_id, ProductModel.is_active)
        )
        return list(result.all())

    async def get_active_by_id(self, product_id: int) -> ProductModel | None:
        result = await self._db.scalars(
            select(ProductModel)
            .options(*_PRODUCT_WITH_CATEGORY)
            .where(ProductModel.id == product_id, ProductModel.is_active)
        )
        return result.first()

    async def get_with_category(self, product_id: int) -> ProductModel | None:
        return await self.get_active_by_id(product_id)

    async def add(self, product: ProductModel) -> None:
        self._db.add(product)

    async def update_fields(self, product_id: int, data: dict) -> None:
        await self._db.execute(
            update(ProductModel).where(ProductModel.id == product_id).values(**data)
        )

    async def soft_delete(self, product_id: int) -> None:
        await self._db.execute(
            update(ProductModel)
            .where(ProductModel.id == product_id)
            .values(is_active=False)
        )

    async def set_rating(self, product_id: int, rating: float) -> None:
        product = await self._db.get(ProductModel, product_id)
        if product:
            product.rating = rating

    async def commit(self) -> None:
        await self._db.commit()

    async def refresh(self, product: ProductModel) -> None:
        await self._db.refresh(product)
