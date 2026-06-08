from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.watchlist.schemas import WatchlistCreate, WatchlistResponse
from app.watchlist.services import WatchlistService

router = APIRouter(
    prefix="/watchlist",
    tags=["Watchlist"],
)


@router.post(
    "/",
    response_model=WatchlistResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a movie to the watchlist",
)
async def add_to_watchlist(
    data: WatchlistCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await WatchlistService.add_to_watchlist(
        db=db,
        user_id=current_user.id,
        data=data,
    )


@router.get(
    "/",
    response_model=list[WatchlistResponse],
    summary="Get the current user's watchlist",
)
async def get_my_watchlist(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return await WatchlistService.get_user_watchlist(
        db=db,
        user_id=current_user.id,
    )


@router.delete(
    "/{movie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a movie from the watchlist",
)
async def remove_from_watchlist(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    await WatchlistService.remove_from_watchlist(
        db=db,
        user_id=current_user.id,
        movie_id=movie_id,
    )

    return None
