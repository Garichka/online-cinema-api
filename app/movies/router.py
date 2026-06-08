from fastapi import APIRouter, Depends, status
from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.dependencies import get_current_user, RoleChecker
from app.auth.models import UserGroupEnum
from app.movies.schemas import (
    MovieCreate,
    MovieUpdate,
    MovieResponse,
    MovieShortResponse,
    CategoryCreate,
    CategoryResponse,
    TagCreate,
    TagResponse,
)
from app.movies.services import MovieService, CategoryService, TagService

router = APIRouter(prefix="/movies", tags=["Movies"])

admin_permission = Depends(RoleChecker([UserGroupEnum.ADMIN]))
any_user_permission = Depends(get_current_user)


@router.post(
    "/",
    response_model=MovieResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[admin_permission],
)
async def create_movie(movie_data: MovieCreate, db: AsyncSession = Depends(get_db)):
    movie = await MovieService.create_movie(db, movie_data)
    return MovieResponse.model_validate(movie)


@router.get(
    "/", response_model=list[MovieShortResponse], dependencies=[any_user_permission]
)
async def get_movies(
    skip: int = 0,
    limit: int = 20,
    category_id: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    movies = await MovieService.get_movies_list(db, skip, limit, category_id)
    return [MovieShortResponse.model_validate(m) for m in movies]


@router.get(
    "/{movie_id}", response_model=MovieResponse, dependencies=[any_user_permission]
)
async def get_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    movie = await MovieService.get_movie_by_id(db, movie_id)
    return MovieResponse.model_validate(movie)


@router.put(
    "/{movie_id}", response_model=MovieResponse, dependencies=[admin_permission]
)
async def update_movie(
    movie_id: int, update_data: MovieUpdate, db: AsyncSession = Depends(get_db)
):
    movie = await MovieService.update_movie(db, movie_id, update_data)
    return MovieResponse.model_validate(movie)


@router.delete(
    "/{movie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[admin_permission],
)
async def delete_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    await MovieService.delete_movie(db, movie_id)


@router.post(
    "/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[admin_permission],
)
async def create_category(
    category_data: CategoryCreate, db: AsyncSession = Depends(get_db)
):
    category = await CategoryService.create_category(db, category_data)
    return CategoryResponse.model_validate(category)


@router.get(
    "/categories",
    response_model=list[CategoryResponse],
    dependencies=[any_user_permission],
)
async def get_categories(db: AsyncSession = Depends(get_db)):
    return [
        CategoryResponse.model_validate(c)
        for c in await CategoryService.get_all_categories(db)
    ]


@router.post(
    "/tags",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[admin_permission],
)
async def create_tag(tag_data: TagCreate, db: AsyncSession = Depends(get_db)):
    tag = await TagService.create_tag(db, tag_data)
    return TagResponse.model_validate(tag)


@router.get(
    "/tags", response_model=list[TagResponse], dependencies=[any_user_permission]
)
async def get_tags(db: AsyncSession = Depends(get_db)):
    return [TagResponse.model_validate(t) for t in await TagService.get_all_tags(db)]


@router.get("/", response_model=list[MovieResponse])
@cache(expire=60)
async def get_all_movies(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
):
    movies = await MovieService.get_all_movies(db, skip, limit)
    return [MovieResponse.model_validate(m) for m in movies]
