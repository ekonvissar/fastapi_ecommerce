from fastapi import UploadFile

from app.catalog.exceptions import (
    CatalogProductNotFoundError,
    CategoryNotFoundError,
    InactiveCategoryError,
    InvalidPriceRangeError,
    ProductAccessDeniedError,
)
from app.catalog.repositories.category_repository import CategoryRepository
from app.catalog.repositories.product_repository import (
    ProductListFilters,
    ProductRepository,
)
from app.catalog.schemas.product import ProductCreate
from app.catalog.services.image_storage import ImageStorage
from app.models.products import Product as ProductModel


class ProductService:
    def __init__(
        self,
        products: ProductRepository,
        categories: CategoryRepository,
        images: ImageStorage,
    ) -> None:
        self._products = products
        self._categories = categories
        self._images = images

    async def list_products(self, filters: ProductListFilters) -> tuple[list, int]:
        if (
            filters.min_price is not None
            and filters.max_price is not None
            and filters.min_price > filters.max_price
        ):
            raise InvalidPriceRangeError
        return await self._products.list_filtered(filters)

    async def list_by_category(self, category_id: int) -> list[ProductModel]:
        category = await self._categories.get_active_by_id(category_id)
        if category is None:
            raise CategoryNotFoundError
        return await self._products.list_by_category(category_id)

    async def get_product(self, product_id: int) -> ProductModel:
        product = await self._products.get_active_by_id(product_id)
        if product is None:
            raise CatalogProductNotFoundError()

        category = await self._categories.get_by_id(product.category_id)
        if category is None:
            raise InactiveCategoryError("Category not found")
        return product

    async def _ensure_active_category(self, category_id: int) -> None:
        category = await self._categories.get_active_by_id(category_id)
        if category is None:
            raise InactiveCategoryError()

    async def create(
        self,
        data: ProductCreate,
        seller_id: int,
        image: UploadFile | None,
    ) -> ProductModel:
        await self._ensure_active_category(data.category_id)
        image_url = await self._images.save_product_image(image) if image else None

        product = ProductModel(
            **data.model_dump(), seller_id=seller_id, image_url=image_url
        )
        await self._products.add(product)
        await self._products.commit()
        loaded = await self._products.get_with_category(product.id)
        return loaded or product

    async def update(
        self,
        product_id: int,
        data: ProductCreate,
        seller_id: int,
        image: UploadFile | None,
    ) -> ProductModel:
        product = await self._products.get_active_by_id(product_id)
        if product is None:
            raise CatalogProductNotFoundError()

        if product.seller_id != seller_id:
            raise ProductAccessDeniedError("You can only update your own products")

        category = await self._categories.get_active_by_id(data.category_id)
        if category is None:
            raise InactiveCategoryError("Category not found")

        await self._products.update_fields(product_id, data.model_dump())

        if image:
            self._images.remove_product_image(product.image_url)
            product.image_url = await self._images.save_product_image(image)

        await self._products.commit()
        loaded = await self._products.get_with_category(product_id)
        return loaded or product

    async def delete(self, product_id: int, seller_id: int) -> ProductModel:
        product = await self._products.get_active_by_id(product_id)
        if product is None:
            raise CatalogProductNotFoundError()

        if product.seller_id != seller_id:
            raise ProductAccessDeniedError("Only sellers can perform this action")

        await self._products.soft_delete(product_id)
        self._images.remove_product_image(product.image_url)
        await self._products.commit()
        loaded = await self._products.get_with_category(product_id)
        return loaded or product
