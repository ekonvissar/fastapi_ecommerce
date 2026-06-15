from fastapi import APIRouter, Depends, status

from app.catalog.deps import get_category_service, get_product_service
from app.catalog.schemas.category import Category as CategorySchema
from app.catalog.schemas.category import CategoryCreate
from app.catalog.services.category_service import CategoryService
from app.catalog.services.product_service import ProductService
from app.shared.schemas.product import Product as ProductSchema

router = APIRouter(prefix="/categories", tags=["categories"])

category_products_router = APIRouter(prefix="/{category_id}/products")


@router.get("/", response_model=list[CategorySchema])
async def get_categories(service: CategoryService = Depends(get_category_service)):
    return await service.list_categories()


@router.post("/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryCreate,
    service: CategoryService = Depends(get_category_service),
):
    return await service.create(category)


@router.put("/{category_id}", response_model=CategorySchema)
async def update_category(
    category_id: int,
    category: CategoryCreate,
    service: CategoryService = Depends(get_category_service),
):
    return await service.update(category_id, category)


@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
async def delete_category(
    category_id: int,
    service: CategoryService = Depends(get_category_service),
):
    return await service.delete(category_id)


@category_products_router.get("/", response_model=list[ProductSchema])
async def get_products_by_category(
    category_id: int,
    service: ProductService = Depends(get_product_service),
):
    return await service.list_by_category(category_id)


router.include_router(category_products_router)
