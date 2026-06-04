from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.reviews.models import Review
from app.movies.models import Movie
from app.reviews.schemas import ReviewCreate, ReviewUpdate


class ReviewService:
    @staticmethod
    async def _recalculate_movie_rating(db: AsyncSession, movie_id: int) -> None:
        avg_stmt = select(func.avg(Review.rating)).where(Review.movie_id == movie_id)
        avg_res = await db.execute(avg_stmt)
        avg_rating = avg_res.scalar()

        final_rating = round(float(avg_rating), 1) if avg_rating is not None else 0.0

        movie_stmt = select(Movie).where(Movie.id == movie_id)
        movie_res = await db.execute(movie_stmt)
        movie = movie_res.scalar_one_or_none()

        if movie:
            movie.rating = final_rating

    @staticmethod
    async def create_review(
        db: AsyncSession, user_id: int, review_data: ReviewCreate
    ) -> Review:
        movie_stmt = select(Movie).where(Movie.id == review_data.movie_id)
        movie_res = await db.execute(movie_stmt)

        if not movie_res.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found."
            )

        existing_stmt = select(Review).where(
            Review.user_id == user_id, Review.movie_id == review_data.movie_id
        )
        existing_res = await db.execute(existing_stmt)

        if existing_res.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already reviewed this movie. You can only edit it.",
            )

        new_review = Review(user_id=user_id, **review_data.model_dump())
        db.add(new_review)

        await db.flush()
        await ReviewService._recalculate_movie_rating(db, review_data.movie_id)

        await db.commit()
        await db.refresh(new_review)
        return new_review

    @staticmethod
    async def get_movie_reviews(
        db: AsyncSession, movie_id: int, skip: int = 0, limit: int = 10
    ) -> list[Review]:
        stmt = (
            select(Review)
            .where(Review.movie_id == movie_id)
            .order_by(Review.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def update_review(
        db: AsyncSession, review_id: int, user_id: int, update_data: ReviewUpdate
    ) -> Review:
        stmt = select(Review).where(Review.id == review_id)
        res = await db.execute(stmt)
        review = res.scalar_one_or_none()

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Review not found."
            )

        if review.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only edit your own reviews.",
            )

        data = update_data.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(review, key, value)

        await db.flush()
        await ReviewService._recalculate_movie_rating(db, review.movie_id)

        await db.commit()
        await db.refresh(review)
        return review

    @staticmethod
    async def delete_review(
        db: AsyncSession, review_id: int, user_id: int, is_admin: bool = False
    ) -> None:
        stmt = select(Review).where(Review.id == review_id)
        res = await db.execute(stmt)
        review = res.scalar_one_or_none()

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Review not found."
            )

        if review.user_id != user_id and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to delete this review.",
            )

        movie_id = review.movie_id
        await db.delete(review)
        await db.flush()

        await ReviewService._recalculate_movie_rating(db, movie_id)
        await db.commit()
