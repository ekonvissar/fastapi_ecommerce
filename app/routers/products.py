from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import Product as ProductSchema
from app.schemas import ProductCreate
from app.models.products import Product as ProductModel
from app.models.categories import Category as CategoryModel
from app.db_depends import get_async_db


router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/", response_model=list[ProductSchema])
async def get_all_products(db: AsyncSession = Depends(get_async_db)):

    result = await db.scalars(select(ProductModel)
                          .where(ProductModel.is_active == True))
    return  result.all()


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_async_db)):

    category_result = await db.scalars(select(CategoryModel)
                              .where(CategoryModel.id == product.category_id,
                                     CategoryModel.is_active == True))
    category = category_result.first()
    if not category:
        raise HTTPException(status_code=400, detail="Category not found")

    db_product = ProductModel(**product.model_dump())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product


@router.get("/category/{category_id}", response_model=list[ProductSchema])
async def get_products_by_category(category_id: int, db: AsyncSession = Depends(get_async_db)):

    category_result = await db.scalars(select(CategoryModel)
                                       .where(CategoryModel.id == category_id,
                                              CategoryModel.is_active == True))
    category = category_result.first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    product_result = await db.scalars(select(ProductModel)
                                      .where(ProductModel.category_id == category_id,
                                             ProductModel.is_active == True))
    product = product_result.all()

    return product


@router.get("/{product_id}", response_model=ProductSchema)
async def get_product(product_id: int, db: AsyncSession = Depends(get_async_db)):

    product_result = await db.scalars(
        select(ProductModel).where(ProductModel.id == product_id,
                                   ProductModel.is_active == True)
    )
    product = product_result.first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not fount")

    category_result = await db.scalars(
        select(CategoryModel).where(CategoryModel.id == product.category_id)
    )
    category = category_result.first()
    if not category:
        raise HTTPException(status_code=400, detail="Category not found")

    return product


@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(product_id: int, product: ProductCreate, db: AsyncSession = Depends(get_async_db)):

    product_result = await db.scalars(
        select(ProductModel).where(ProductModel.id == product_id,
               ProductModel.is_active == True)
    )
    product_data = product_result.first()
    if not product_data:
        raise HTTPException(status_code=404, detail="Product not found")

    category_result = await db.scalars(
        select(ProductModel).where(ProductModel.category_id == product.category_id,
                                   ProductModel.is_active == True)
    )
    category_data = category_result.first()
    if not category_data:
        raise HTTPException(status_code=400, detail="Category not found")

    await db.execute(
        update(ProductModel)
        .where(ProductModel.id == product_id)
        .values(**product.model_dump()))
    await db.commit()
    return  product_data


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_async_db)):

    product_result = await db.scalars(
        select(ProductModel).where(ProductModel.id == product_id,
                                   ProductModel.is_active == True)
    )
    product = product_result.first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.is_active = False
    await db.commit()
    return product