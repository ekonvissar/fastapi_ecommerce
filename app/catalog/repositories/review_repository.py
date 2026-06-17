from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.reviews import Review as ReviewModel

_REVIEW_WITH_RELATIONS = (
    selectinload(ReviewModel.user),
    selectinload(ReviewModel.product),
)


class ReviewRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_active(self) -> list[ReviewModel]:
        result = await self._db.scalars(
            select(ReviewModel)
            .options(*_REVIEW_WITH_RELATIONS)
            .where(ReviewModel.is_active)
        )
        return list(result.all())

    async def list_by_product(self, product_id: int) -> list[ReviewModel]:
        result = await self._db.scalars(
            select(ReviewModel)
            .options(*_REVIEW_WITH_RELATIONS)
            .where(ReviewModel.product_id == product_id, ReviewModel.is_active)
        )
        return list(result.all())

    async def get_active_by_id(self, review_id: int) -> ReviewModel | None:
        result = await self._db.scalars(
            select(ReviewModel)
            .options(*_REVIEW_WITH_RELATIONS)
            .where(ReviewModel.id == review_id, ReviewModel.is_active)
        )
        return result.first()

    async def get_with_relations(self, review_id: int) -> ReviewModel | None:
        result = await self._db.scalars(
            select(ReviewModel)
            .options(*_REVIEW_WITH_RELATIONS)
            .where(ReviewModel.id == review_id)
        )
        return result.first()

    async def add(self, review: ReviewModel) -> None:
        self._db.add(review)

    async def avg_grade_for_product(self, product_id: int) -> float:
        result = await self._db.execute(
            select(func.avg(ReviewModel.grade)).where(
                ReviewModel.product_id == product_id, ReviewModel.is_active
            )
        )
        return float(result.scalar() or 0.0)

    async def commit(self) -> None:
        await self._db.commit()

    async def refresh(self, review: ReviewModel) -> None:
        await self._db.refresh(review)
