from app.catalog.exceptions import CatalogProductNotFoundError, ReviewNotFoundError
from app.catalog.repositories.product_repository import ProductRepository
from app.catalog.repositories.review_repository import ReviewRepository
from app.catalog.schemas.review import ReviewCreate
from app.models.reviews import Review as ReviewModel


class ReviewService:
    def __init__(
        self,
        reviews: ReviewRepository,
        products: ProductRepository,
    ) -> None:
        self._reviews = reviews
        self._products = products

    async def list_reviews(self) -> list[ReviewModel]:
        return await self._reviews.list_active()

    async def list_by_product(self, product_id: int) -> list[ReviewModel]:
        product = await self._products.get_active_by_id(product_id)
        if product is None:
            raise CatalogProductNotFoundError()
        return await self._reviews.list_by_product(product_id)

    async def create(self, data: ReviewCreate, user_id: int) -> ReviewModel:
        product = await self._products.get_active_by_id(data.product_id)
        if product is None:
            raise CatalogProductNotFoundError()

        review = ReviewModel(**data.model_dump(), user_id=user_id)
        await self._reviews.add(review)
        await self._reviews.commit()
        loaded = await self._reviews.get_with_relations(review.id)
        await self._update_product_rating(data.product_id)
        return loaded or review

    async def delete(self, review_id: int) -> dict[str, str]:
        review = await self._reviews.get_active_by_id(review_id)
        if review is None:
            raise ReviewNotFoundError()

        review.is_active = False
        await self._reviews.commit()
        await self._reviews.refresh(review)
        await self._update_product_rating(review.product_id)
        return {"message": "Review deleted"}

    async def _update_product_rating(self, product_id: int) -> None:
        avg_rating = await self._reviews.avg_grade_for_product(product_id)
        product = await self._products.get_active_by_id(product_id)
        if product is None:
            raise CatalogProductNotFoundError()
        await self._products.set_rating(product_id, avg_rating)
        await self._products.commit()
