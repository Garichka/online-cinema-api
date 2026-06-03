from datetime import datetime

from pydantic import BaseModel, Field, field_validator, HttpUrl, ConfigDict


class TagBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Tag name")


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Category name")

    description: str | None = Field(None, description="Category description")


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class MovieBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Movie title")

    description: str = Field(..., description="Detailed movie description")

    release_year: int = Field(
        ..., ge=1888, description="Release year (must not be earlier than 1888)"
    )

    duration: int = Field(..., gt=0, description="Movie duration in minutes")

    rating: float = Field(
        default=0.0, ge=0.0, le=10.0, description="Movie rating (0.0 - 10.0)"
    )

    poster_url: HttpUrl = Field(
        ..., description="Valid HTTP/HTTPS URL to the movie poster"
    )

    video_url: HttpUrl = Field(
        ..., description="Valid HTTP/HTTPS URL to the movie video file"
    )

    category_id: int = Field(
        ..., gt=0, description="Category ID (must be greater than 0)"
    )

    @field_validator("release_year")
    @classmethod
    def validate_release_year(cls, value: int) -> int:
        current_year = datetime.now().year

        if value > current_year + 5:
            raise ValueError(f"Release year cannot be greater than {current_year + 5}")

        return value


class MovieCreate(MovieBase):
    tag_ids: list[int] = Field(default_factory=list, description="List of tag IDs")

    @field_validator("tag_ids")
    @classmethod
    def validate_tag_ids(cls, value: list[int]) -> list[int]:
        if any(tag_id <= 0 for tag_id in value):
            raise ValueError("Tag IDs must be greater than 0")

        return list(set(value))


class MovieUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    release_year: int | None = Field(None, ge=1888)
    duration: int | None = Field(None, gt=0)
    rating: float | None = Field(None, ge=0.0, le=10.0)
    poster_url: HttpUrl | None = None
    video_url: HttpUrl | None = None
    category_id: int | None = Field(None, gt=0)
    tag_ids: list[int] | None = None

    @field_validator("release_year")
    @classmethod
    def validate_release_year_update(cls, value: int | None) -> int | None:
        if value is None:
            return value

        current_year = datetime.now().year

        if value > current_year + 5:
            raise ValueError(f"Release year cannot be greater than {current_year + 5}")

        return value

    @field_validator("tag_ids")
    @classmethod
    def validate_tag_ids_update(cls, value: list[int] | None) -> list[int] | None:
        if value is None:
            return value

        if any(tag_id <= 0 for tag_id in value):
            raise ValueError("Tag IDs must be greater than 0")

        return list(set(value))


class MovieShortResponse(BaseModel):
    id: int
    title: str
    rating: float
    poster_url: HttpUrl

    model_config = ConfigDict(from_attributes=True)


class MovieResponse(MovieBase):
    id: int
    created_at: datetime
    updated_at: datetime

    category: CategoryResponse
    tags: list[TagResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
