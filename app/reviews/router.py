from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User, UserGroupEnum
from app.reviews.schemas import ReviewCreate, ReviewUpdate, ReviewResponse
from app.reviews.services import ReviewService

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = await ReviewService.create_review(db, current_user.id, review_data)
    return ReviewResponse.model_validate(review)


@router.get("/movie/{movie_id}", response_model=list[ReviewResponse])
async def get_reviews(
    movie_id: int,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    reviews = await ReviewService.get_movie_reviews(db, movie_id, skip, limit)
    return [ReviewResponse.model_validate(r) for r in reviews]


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: int,
    update_data: ReviewUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = await ReviewService.update_review(
        db, review_id, current_user.id, update_data
    )
    return ReviewResponse.model_validate(review)


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    is_admin = current_user.group == UserGroupEnum.ADMIN
    await ReviewService.delete_review(db, review_id, current_user.id, is_admin)
