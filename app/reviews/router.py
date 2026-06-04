from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User, UserGroupEnum
from app.reviews.schemas import ReviewCreate, ReviewUpdate, ReviewResponse
from app.reviews.services import ReviewService

router = APIRouter(prefix="/reviews", tags=["Reviews & Ratings"])


@router.post(
    "/",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a review and rating for a movie",
)
async def create_review(
    review_data: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await ReviewService.create_review(
        db=db, user_id=current_user.id, review_data=review_data
    )


@router.get(
    "/movie/{movie_id}",
    response_model=list[ReviewResponse],
    summary="Get list of reviews for a specific movie",
)
async def get_movie_reviews(
    movie_id: int,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await ReviewService.get_movie_reviews(
        db=db, movie_id=movie_id, skip=skip, limit=limit
    )


@router.put(
    "/{review_id}", response_model=ReviewResponse, summary="Update your own review"
)
async def update_review(
    review_id: int,
    update_data: ReviewUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await ReviewService.update_review(
        db=db, review_id=review_id, user_id=current_user.id, update_data=update_data
    )


@router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a review (Owner or Admin)",
)
async def delete_review(
    review_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    is_admin = current_user.group == UserGroupEnum.ADMIN

    await ReviewService.delete_review(
        db=db, review_id=review_id, user_id=current_user.id, is_admin=is_admin
    )

    return None
