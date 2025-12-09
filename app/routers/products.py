from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import Product as ProductSchema, ProductCreate, ProductList
from app.models.products import Product as ProductModel
from app.models.categories import Category as CategoryModel
from app.models.users import User as UserModel
from app.db_depends import get_async_db
from app.auth import get_current_seller


router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/", response_model=ProductList)
async def get_all_products(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        category_id: int | None = Query(
            None, description="ID категории для фильтрации"),
        min_price: float | None = Query(
            None, ge=0, description="Минимальная цена товара"),
        max_price: float | None = Query(
            None, ge=0, description="Максимальная цена товара"),
        in_stock: bool | None = Query(
            None, description="true — только товары в наличии, false — только без остатка"),
        seller_id: int | None = Query(
            None, description="ID продавца для фильтрации"),
        db: AsyncSession = Depends(get_async_db),
):
    """
    Возвращает список всех активных товаров с поддержкой фильтров.
    """
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_price не может быть больше max_price",
        )

    filters = [ProductModel.is_active == True]

    if category_id is not None:
        filters.append(ProductModel.category_id == category_id)
    if min_price is not None:
        filters.append(ProductModel.price >= min_price)
    if max_price is not None:
        filters.append(ProductModel.price <= max_price)
    if in_stock is not None:
        filters.append(ProductModel.stock > 0 if in_stock else ProductModel.stock == 0)
    if seller_id is not None:
        filters.append(ProductModel.seller_id == seller_id)

    total_stmt = select(func.count()).select_from(ProductModel).where(*filters)
    total = await db.scalar(total_stmt) or 0

    products_stmt = (
        select(ProductModel)
        .where(*filters)
        .order_by(ProductModel.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = (await db.scalars(products_stmt)).all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
        product: ProductCreate,
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_seller)
):

    category_result = await db.scalars(select(CategoryModel)
                              .where(CategoryModel.id == product.category_id,
                                     CategoryModel.is_active == True))
    category = category_result.first()
    if not category:
        raise HTTPException(status_code=400, detail="Category not found")

    db_product = ProductModel(**product.model_dump(), seller_id=current_user.id)
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
async def update_product(
        product_id: int,
        product: ProductCreate,
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_seller)):

    product_result = await db.scalars(
        select(ProductModel).where(ProductModel.id == product_id,
               ProductModel.is_active == True)
    )
    product_data = product_result.first()
    if not product_data:
        raise HTTPException(status_code=404, detail="Product not found")

    if product_data.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only sellers can perform this action")

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
async def delete_product(
        product_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_seller)):

    product_result = await db.scalars(
        select(ProductModel).where(ProductModel.id == product_id,
                                   ProductModel.is_active == True)
    )
    product = product_result.first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only sellers can perform this action")

    product.is_active = False
    await db.commit()
    await db.refresh(product)
    return product