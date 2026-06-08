from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.movies.schemas import MovieShortResponse


class WatchlistCreate(BaseModel):
    movie_id: int = Field(
        ..., gt=0, description="ID of the movie the user wants to add to the watchlist"
    )


class WatchlistResponse(BaseModel):
    id: int
    user_id: int
    added_at: datetime
    movie: MovieShortResponse

    model_config = ConfigDict(from_attributes=True)
