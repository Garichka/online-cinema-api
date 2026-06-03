from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.movies.models import Movie, Category, Tag
from app.movies.schemas import MovieCreate, MovieUpdate, CategoryCreate, TagCreate


class MovieService:
    @staticmethod
    async def create_movie(db: AsyncSession, movie_data: MovieCreate) -> Movie:
        category_stmt = select(Category).where(Category.id == movie_data.category_id)
        category_result = await db.execute(category_stmt)

        if not category_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with ID {movie_data.category_id} not found.",
            )

        db_tags = []
        unique_tag_ids = set(movie_data.tag_ids)

        if unique_tag_ids:
            tags_stmt = select(Tag).where(Tag.id.in_(unique_tag_ids))
            tags_result = await db.execute(tags_stmt)
            db_tags = list(tags_result.scalars().all())

            if len(db_tags) != len(unique_tag_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="One or more specified tags do not exist in the system.",
                )

        movie_dict = movie_data.model_dump(exclude={"tag_ids"})
        movie_dict["poster_url"] = str(movie_dict["poster_url"])
        movie_dict["video_url"] = str(movie_dict["video_url"])

        new_movie = Movie(**movie_dict)
        new_movie.tags = db_tags

        db.add(new_movie)
        await db.commit()

        return await MovieService.get_movie_by_id(db, new_movie.id)

    @staticmethod
    async def get_movie_by_id(db: AsyncSession, movie_id: int) -> Movie:
        stmt = (
            select(Movie)
            .options(selectinload(Movie.category), selectinload(Movie.tags))
            .where(Movie.id == movie_id)
        )

        result = await db.execute(stmt)
        movie = result.scalar_one_or_none()

        if not movie:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Movie with ID {movie_id} not found.",
            )

        return movie

    @staticmethod
    async def get_movies_list(
        db: AsyncSession, skip: int = 0, limit: int = 20, category_id: int | None = None
    ) -> list[Movie]:

        stmt = select(Movie).options(
            selectinload(Movie.category), selectinload(Movie.tags)
        )

        if category_id:
            stmt = stmt.where(Movie.category_id == category_id)

        stmt = stmt.order_by(Movie.id.desc()).offset(skip).limit(limit)

        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def update_movie(
        db: AsyncSession, movie_id: int, update_data: MovieUpdate
    ) -> Movie:

        movie = await MovieService.get_movie_by_id(db, movie_id)
        data_to_update = update_data.model_dump(exclude_unset=True)

        cat_id = data_to_update.get("category_id")
        if cat_id is not None:
            cat_stmt = select(Category).where(Category.id == cat_id)
            cat_res = await db.execute(cat_stmt)

            if not cat_res.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Specified category does not exist.",
                )

        if "tag_ids" in data_to_update:
            tag_ids = data_to_update.pop("tag_ids")

            if tag_ids is not None:
                unique_tag_ids = set(tag_ids)

                if unique_tag_ids:
                    tags_stmt = select(Tag).where(Tag.id.in_(unique_tag_ids))
                    tags_result = await db.execute(tags_stmt)
                    db_tags = list(tags_result.scalars().all())

                    if len(db_tags) != len(unique_tag_ids):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="One or more tags were not found.",
                        )

                    movie.tags = db_tags
                else:
                    movie.tags = []

        for key, value in data_to_update.items():
            if value is not None:
                if key in ["poster_url", "video_url"]:
                    value = str(value)
                setattr(movie, key, value)

        await db.commit()
        await db.refresh(movie)
        return movie

    @staticmethod
    async def delete_movie(db: AsyncSession, movie_id: int) -> None:
        stmt = select(Movie).where(Movie.id == movie_id)
        result = await db.execute(stmt)
        movie = result.scalar_one_or_none()

        if not movie:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Movie with ID {movie_id} not found.",
            )

        await db.delete(movie)
        await db.commit()


class CategoryService:
    @staticmethod
    async def create_category(
        db: AsyncSession, category_data: CategoryCreate
    ) -> Category:

        stmt = select(Category).where(Category.name == category_data.name)
        res = await db.execute(stmt)

        if res.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with name '{category_data.name}' already exists.",
            )

        new_category = Category(**category_data.model_dump())
        db.add(new_category)
        await db.commit()
        await db.refresh(new_category)
        return new_category

    @staticmethod
    async def get_all_categories(db: AsyncSession) -> list[Category]:

        stmt = select(Category).order_by(Category.name.asc())
        result = await db.execute(stmt)
        return list(result.scalars().all())


class TagService:
    @staticmethod
    async def create_tag(db: AsyncSession, tag_data: TagCreate) -> Tag:

        stmt = select(Tag).where(Tag.name == tag_data.name)
        res = await db.execute(stmt)

        if res.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tag with name '{tag_data.name}' already exists.",
            )

        new_tag = Tag(**tag_data.model_dump())
        db.add(new_tag)
        await db.commit()
        await db.refresh(new_tag)
        return new_tag

    @staticmethod
    async def get_all_tags(db: AsyncSession) -> list[Tag]:

        stmt = select(Tag).order_by(Tag.name.asc())
        result = await db.execute(stmt)
        return list(result.scalars().all())
