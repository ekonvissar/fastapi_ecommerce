from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, update

from app.schemas import Product as ProductSchema
from app.schemas import ProductCreate
from app.models.products import Product as ProductModel
from app.models.categories import Category as CategoryModel
from app.db_depends import get_db


# Создаём маршрутизатор для товаров
router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/", response_model=list[ProductSchema])
async def get_all_products(db: Session = Depends(get_db)):
    """
    Возвращает список всех товаров.
    """
    products = db.scalars(select(ProductModel)
                          .where(ProductModel.is_active == True)).all()
    return  products


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """
    Создаёт новый товар.
    """
    stmt = select(CategoryModel).where(CategoryModel.id == product.category_id,
                                       CategoryModel.is_active == True)
    category = db.scalars(stmt).first()
    if not category:
        raise HTTPException(status_code=400, detail="Category not found")

    db_product = ProductModel(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/category/{category_id}", response_model=list[ProductSchema])
async def get_products_by_category(category_id: int, db: Session = Depends(get_db)):
    """
    Возвращает список товаров в указанной категории по её ID.
    """
    category_stmt = select(CategoryModel).where(CategoryModel.id == category_id,
                                       CategoryModel.is_active == True)
    category = db.scalars(category_stmt).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    product_stmt = select(ProductModel).where(ProductModel.category_id == category_id,
                                              ProductModel.is_active == True)
    product = db.scalars(product_stmt).all()

    return product


@router.get("/{product_id}", response_model=ProductSchema)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Возвращает детальную информацию о товаре по его ID.
    """
    product = db.scalars(
        select(ProductModel).where(ProductModel.id == product_id,
                                   ProductModel.is_active == True)
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not fount")

    category = db.scalars(
        select(CategoryModel).where(CategoryModel.id == product.category_id)
    ).first()
    if not category:
        raise HTTPException(status_code=400, detail="Category not found")

    return product


@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_db)):
    """
    Обновляет товар по его ID.
    """
    product_stmt = db.scalars(
        select(ProductModel).where(ProductModel.id == product_id,
               ProductModel.is_active == True)
    ).first()
    if not product_stmt:
        raise HTTPException(status_code=404, detail="Product not found")

    category_stmt = db.scalars(
        select(ProductModel).where(ProductModel.category_id == product.category_id,
                                   ProductModel.is_active == True)
    ).first()
    if not category_stmt:
        raise HTTPException(status_code=400, detail="Category not found")

    db.execute(update(ProductModel).where(ProductModel.id == product_id,)
               .values(**product.model_dump()))
    db.commit()
    db.refresh(product_stmt)
    return  product_stmt


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """
    Удаляет товар по его ID.
    """
    product = db.scalars(
        select(ProductModel).where(ProductModel.id == product_id,
                                   ProductModel.is_active == True)
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")


    db.execute(update(ProductModel)
               .where(ProductModel.id == product_id,
                      ProductModel.is_active == True)
               .values(is_active=False))
    db.commit()
    return {"status": "success", "message": "Product marked as inactive"}