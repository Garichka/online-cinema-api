from fastapi import APIRouter, Depends, status
from fastapi_cache.decorator import cache

from app.core.database import get_db
from app.auth.dependencies import get_current_user, RoleChecker
from app.auth.models import UserGroupEnum
from app.movies.schemas import (
    MovieCreate,
    MovieUpdate,
    MovieResponse,
    MovieShortResponse,
    TagResponse,
    TagCreate,
    CategoryResponse,
    CategoryCreate,
)
from app.movies.services import MovieService, TagService, CategoryService

from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/movies", tags=["Movies"])

admin_permission = Depends(RoleChecker([UserGroupEnum.ADMIN]))
any_user_permission = Depends(get_current_user)


@router.post(
    "/",
    response_model=MovieResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[admin_permission],
    summary="Create a new movie (Admin only)",
)
async def create_movie(
    movie_data: MovieCreate,
    db: AsyncSession = Depends(get_db),
):
    return await MovieService.create_movie(db=db, movie_data=movie_data)


@router.get(
    "/",
    response_model=list[MovieShortResponse],
    dependencies=[any_user_permission],
    summary="Get movies list with pagination and filtering",
)
async def get_movies(
    skip: int = 0,
    limit: int = 20,
    category_id: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await MovieService.get_movies_list(
        db=db,
        skip=skip,
        limit=limit,
        category_id=category_id,
    )


@router.get(
    "/{movie_id}",
    response_model=MovieResponse,
    dependencies=[any_user_permission],
    summary="Get full movie details by ID",
)
async def get_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await MovieService.get_movie_by_id(db=db, movie_id=movie_id)


@router.put(
    "/{movie_id}",
    response_model=MovieResponse,
    dependencies=[admin_permission],
    summary="Update movie data (Admin only)",
)
async def update_movie(
    movie_id: int,
    update_data: MovieUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await MovieService.update_movie(
        db=db,
        movie_id=movie_id,
        update_data=update_data,
    )


@router.delete(
    "/{movie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[admin_permission],
    summary="Delete movie (Admin only)",
)
async def delete_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
):
    await MovieService.delete_movie(db=db, movie_id=movie_id)


@router.post(
    "/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[admin_permission],
    summary="Create category (Admin only)",
)
async def create_category(
    category_data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
):
    return await CategoryService.create_category(
        db=db,
        category_data=category_data,
    )


@router.get(
    "/categories",
    response_model=list[CategoryResponse],
    dependencies=[any_user_permission],
    summary="Get all categories",
)
async def get_categories(db: AsyncSession = Depends(get_db)):
    return await CategoryService.get_all_categories(db=db)


@router.post(
    "/tags",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[admin_permission],
    summary="Create tag (Admin only)",
)
async def create_tag(
    tag_data: TagCreate,
    db: AsyncSession = Depends(get_db),
):
    return await TagService.create_tag(
        db=db,
        tag_data=tag_data,
    )


@router.get(
    "/tags",
    response_model=list[TagResponse],
    dependencies=[any_user_permission],
    summary="Get all tags",
)
async def get_tags(db: AsyncSession = Depends(get_db)):
    return await TagService.get_all_tags(db=db)


@router.get(
    "/",
    response_model=list[MovieResponse],
    summary="Get a list of all movies",
)
@cache(expire=60)
async def get_movies(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    return await MovieService.get_all_movies(
        db=db,
        skip=skip,
        limit=limit,
    )
