from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.watchlist.schemas import WatchlistCreate, WatchlistResponse
from app.watchlist.services import WatchlistService

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])


@router.post("/", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED)
async def add_to_watchlist(
    data: WatchlistCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = await WatchlistService.add_to_watchlist(db, current_user.id, data)
    return WatchlistResponse.model_validate(item)


@router.get("/", response_model=list[WatchlistResponse])
async def get_watchlist(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    items = await WatchlistService.get_user_watchlist(db, current_user.id)
    return [WatchlistResponse.model_validate(i) for i in items]


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await WatchlistService.remove_from_watchlist(db, current_user.id, movie_id)
