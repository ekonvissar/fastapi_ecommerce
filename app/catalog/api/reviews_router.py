from fastapi import APIRouter, Depends, status

from app.auth import get_current_admin, get_current_buyer
from app.catalog.deps import get_review_service
from app.catalog.schemas.review import Review as ReviewSchema
from app.catalog.schemas.review import ReviewCreate
from app.catalog.services.review_service import ReviewService
from app.models.users import User as UserModel

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/", response_model=list[ReviewSchema])
async def get_reviews(service: ReviewService = Depends(get_review_service)):
    return await service.list_reviews()


@router.post("/", response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
async def create_review(
    review: ReviewCreate,
    current_user: UserModel = Depends(get_current_buyer),
    service: ReviewService = Depends(get_review_service),
):
    return await service.create(review, current_user.id)


@router.delete("/{review_id}", status_code=status.HTTP_200_OK)
async def delete_review(
    review_id: int,
    current_user: UserModel = Depends(get_current_admin),
    service: ReviewService = Depends(get_review_service),
):
    return await service.delete(review_id)
