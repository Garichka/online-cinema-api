from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=10, description="Movie rating from 1 to 10")
    text: str | None = Field(
        None, max_length=3000, description="Review text (up to 3000 characters)"
    )


class ReviewCreate(ReviewBase):
    movie_id: int = Field(..., gt=0, description="ID of the movie being reviewed")


class ReviewUpdate(BaseModel):
    rating: int | None = Field(None, ge=1, le=10)
    text: str | None = Field(None, max_length=3000)


class ReviewResponse(ReviewBase):
    id: int
    user_id: int
    movie_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
