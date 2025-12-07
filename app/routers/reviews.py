from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_buyer, get_current_admin
from app.schemas import Review as ReviewSchema, ReviewCreate
from app.models import Review as ReviewModel
from app.models import Product as ProductModel
from app.models import User as UserModel
from app.db_depends import get_async_db

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
)

@router.get("/", response_model=list[ReviewSchema])
async def get_reviews(db: AsyncSession = Depends(get_async_db)):
    reviews = await db.scalars(select(ReviewModel).where(ReviewModel.is_active == True))
    reviews = reviews.all()

    return reviews

@router.get("/product/{product_id}", response_model=list[ReviewSchema])
async def get_reviews_by_product(product_id: int, db: AsyncSession = Depends(get_async_db)):
    product = await db.scalars(select(ProductModel).where(ProductModel.id == product_id,
                                                   ProductModel.is_active == True))
    product = product.first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    reviews_result = await db.scalars(select(ReviewModel).where(ReviewModel.product_id == product_id,
                                                                ReviewModel.is_active == True))
    reviews = reviews_result.all()

    return reviews

@router.post("/", response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
async def create_review(review: ReviewCreate,
                        current_user: UserModel = Depends(get_current_buyer),
                        db: AsyncSession = Depends(get_async_db)):
    product = await db.scalars(select(ProductModel).where(ProductModel.id == review.product_id,
                                                                 ProductModel.is_active == True))
    product = product.first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")


    db_review = ReviewModel(**review.model_dump(), user_id=current_user.id)
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)

    await update_product_rating(db, product.id)

    return db_review

@router.delete("/{review_id}", status_code=status.HTTP_200_OK)
async def delete_review(review_id: int,
                        current_user: UserModel = Depends(get_current_admin),
                        db: AsyncSession = Depends(get_async_db)):
    review_result = await db.scalars(select(ReviewModel).where(ReviewModel.id == review_id,
                                                              ReviewModel.is_active == True))
    review = review_result.first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")


    review.is_active = False
    await db.commit()
    await db.refresh(review)

    await update_product_rating(db, review.product_id)

    return {"message": "Review deleted"}



async def update_product_rating(db: AsyncSession, product_id: int):
    result = await db.execute(
        select(func.avg(ReviewModel.grade)).where(
            ReviewModel.product_id == product_id,
            ReviewModel.is_active == True
        )
    )
    avg_rating = result.scalar() or 0.0
    product = await db.get(ProductModel, product_id)
    product.rating = avg_rating
    await db.commit()

