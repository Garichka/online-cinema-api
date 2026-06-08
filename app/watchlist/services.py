from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import desc

from app.watchlist.models import Watchlist
from app.movies.models import Movie
from app.watchlist.schemas import WatchlistCreate


class WatchlistService:
    @staticmethod
    async def add_to_watchlist(
        db: AsyncSession,
        user_id: int,
        data: WatchlistCreate,
    ) -> Watchlist:

        movie_stmt = select(Movie).where(Movie.id == data.movie_id)
        movie_res = await db.execute(movie_stmt)

        if not movie_res.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie with the specified ID was not found.",
            )

        existing_stmt = select(Watchlist).where(
            Watchlist.user_id == user_id,
            Watchlist.movie_id == data.movie_id,
        )
        existing_res = await db.execute(existing_stmt)

        if existing_res.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This movie is already in your watchlist.",
            )

        new_item = Watchlist(
            user_id=user_id,
            movie_id=data.movie_id,
        )

        db.add(new_item)
        await db.commit()
        await db.refresh(new_item)

        return new_item

    @staticmethod
    async def remove_from_watchlist(
        db: AsyncSession,
        user_id: int,
        movie_id: int,
    ) -> None:

        stmt = select(Watchlist).where(
            Watchlist.user_id == user_id,
            Watchlist.movie_id == movie_id,
        )
        res = await db.execute(stmt)
        item = res.scalar_one_or_none()

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie not found in your watchlist.",
            )

        await db.delete(item)
        await db.commit()

    @staticmethod
    async def get_user_watchlist(
        db: AsyncSession,
        user_id: int,
    ) -> list[Watchlist]:

        stmt = (
            select(Watchlist)
            .options(selectinload(Watchlist.movie))
            .where(Watchlist.user_id == user_id)
            .order_by(desc(Watchlist.id))
        )

        res = await db.execute(stmt)
        return list(res.scalars().all())
