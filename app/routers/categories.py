from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_depends import get_async_db
from app.models.categories import Category as CategoryModel
from app.models import Product as ProductModel
from app.schemas import Category as CategorySchema, CategoryCreate, ProductList

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)


@router.get("/", response_model=ProductList)
async def get_all_categories(page: int = Query(1, ge=1),
                             page_size: int = Query(20, ge=1, le=100),
                             category_id: int | None = Query(
                                 None, description="ID категории для фильтрации"),
                             min_price: int | None = Query(
                                 None, ge=0, description="Минимальная цена товара"),
                             max_price: int | None = Query(
                                 None, ge=0, description="Максимальная цена товара"),
                             in_stock: bool | None = Query(
                                 None, description="true — только товары в наличии, false — только без остатка"),
                             seller_id: int | None = Query(
                                 None, description="ID продавца для фильтрации"),
                             db: AsyncSession = Depends(get_async_db)):
        """
        Возвращает список всех активных товаров с поддержкой фильтров.
        """
        if min_price is not None and max_price is not None and min_price > max_price:
            raise HTTPException(status_code=400, detail="min_price не может быть больше max_price")

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

        product_stmt = (
            select(ProductModel)
            .where(*filters)
            .order_by(ProductModel.id)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        items = (await db.scalars(product_stmt)).all()

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }




@router.post("/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate, db: AsyncSession = Depends(get_async_db)):

    if category.parent_id is not None:
        stmt = select(CategoryModel).where(CategoryModel.id == category.parent_id,
                                           CategoryModel.is_active == True)
        result = await db.scalars(stmt)
        parent = result.first()
        if parent is None:
            raise HTTPException(status_code=400, detail="Parent category not found")

    db_category = CategoryModel(**category.model_dump())
    db.add(db_category)
    await db.commit()
    return db_category


@router.put("/{category_id}", response_model=CategorySchema)
async def update_category(category_id: int, category: CategoryCreate, db: AsyncSession = Depends(get_async_db)):

    stmt = select(CategoryModel).where(CategoryModel.id == category_id,
                                       CategoryModel.is_active == True)
    result = await db.scalars(stmt)
    db_category = result.first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    if category.parent_id is not None:
        parent_stmt = select(CategoryModel).where(CategoryModel.id == category.parent_id,
                                                  CategoryModel.is_active == True)
        parent_result = await db.scalars(parent_stmt)
        parent = parent_result.first()
        if not parent:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parent category not found")
        if parent.id == category_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category cannot be its own parent")

    update_data = category.model_dump(exclude_unset=True)
    await db.execute(
        update(CategoryModel)
        .where(CategoryModel.id == category_id)
        .values(**update_data)
    )
    await db.commit()
    return db_category



@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_async_db)):

    stmt = select(CategoryModel).where(CategoryModel.id == category_id,
                                       CategoryModel.is_active == True)
    result = await db.scalars(stmt)
    category = result.first()
    if not category:
        return HTTPException(status_code=404, detail="Category not found")

    await db.execute(update(CategoryModel)
                     .where(CategoryModel.id == category_id)
                     .values(is_active=False)
                     )
    await db.commit()

    return category
