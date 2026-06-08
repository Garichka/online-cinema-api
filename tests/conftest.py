import asyncio
import uuid

import pytest
from fastapi.testclient import TestClient
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.auth.models import User, UserGroup, UserGroupEnum
from app.core.database import Base, get_db
from app.main import app
from app.movies.models import Category, Movie

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def override_get_db():
    async with TestingSessionLocal() as db:
        yield db


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    async def _create():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await conn.execute(
                insert(UserGroup)
                .prefix_with("OR IGNORE")
                .values(
                    [
                        {"id": 1, "name": UserGroupEnum.USER},
                        {"id": 2, "name": UserGroupEnum.MODERATOR},
                        {"id": 3, "name": UserGroupEnum.ADMIN},
                    ]
                )
            )

    async def _drop():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    asyncio.run(_create())
    FastAPICache.init(InMemoryBackend(), prefix="test-cache")
    yield
    asyncio.run(_drop())


@pytest.fixture
def client():
    return TestClient(app)


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------


def register_and_activate(client, email: str, password: str = "TestPass123!") -> None:
    client.post("/auth/register", json={"email": email, "password": password})

    async def _activate():
        async with TestingSessionLocal() as db:
            await db.execute(
                update(User).where(User.email == email).values(is_active=True)
            )
            await db.commit()

    asyncio.run(_activate())


def get_auth_headers(client, email: str | None = None) -> dict[str, str]:
    if email is None:
        email = f"user_{uuid.uuid4().hex[:8]}@test.com"
    register_and_activate(client, email)
    login = client.post(
        "/auth/login", json={"email": email, "password": "TestPass123!"}
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers(client) -> dict[str, str]:
    return get_auth_headers(client)


@pytest.fixture
def user_in_db(client) -> dict:
    email = f"user_{uuid.uuid4().hex[:8]}@test.com"
    register_and_activate(client, email)

    async def _get_id() -> int:
        async with TestingSessionLocal() as db:
            result = await db.execute(select(User).where(User.email == email))
            return result.scalar_one().id

    user_id = asyncio.run(_get_id())
    login = client.post(
        "/auth/login", json={"email": email, "password": "TestPass123!"}
    )
    token = login.json()["access_token"]
    return {
        "id": user_id,
        "email": email,
        "headers": {"Authorization": f"Bearer {token}"},
    }


# ---------------------------------------------------------------------------
# DB fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def movie_in_db() -> int:
    async def _create() -> int:
        async with TestingSessionLocal() as db:
            cat_res = await db.execute(
                select(Category).where(Category.name == "Test Category")
            )
            category = cat_res.scalar_one_or_none()
            if not category:
                category = Category(name="Test Category", description="For tests")
                db.add(category)
                await db.flush()

            movie = Movie(
                title=f"Test Movie {uuid.uuid4().hex[:6]}",
                description="A test movie",
                release_year=2020,
                duration=120,
                rating=7.5,
                poster_url="http://example.com/poster.jpg",
                video_url="http://example.com/video.mp4",
                category_id=category.id,
            )
            db.add(movie)
            await db.commit()
            await db.refresh(movie)
            return movie.id

    return asyncio.run(_create())


@pytest.fixture
def two_movies_in_db() -> tuple[int, int]:
    async def _create() -> tuple[int, int]:
        async with TestingSessionLocal() as db:
            cat_res = await db.execute(
                select(Category).where(Category.name == "Test Category")
            )
            category = cat_res.scalar_one_or_none()
            if not category:
                category = Category(name="Test Category", description="For tests")
                db.add(category)
                await db.flush()

            tag = uuid.uuid4().hex[:4]
            movie1 = Movie(
                title=f"Movie A {tag}",
                description="First",
                release_year=2020,
                duration=120,
                rating=7.0,
                poster_url="http://example.com/p1.jpg",
                video_url="http://example.com/v1.mp4",
                category_id=category.id,
            )
            movie2 = Movie(
                title=f"Movie B {tag}",
                description="Second",
                release_year=2021,
                duration=90,
                rating=8.0,
                poster_url="http://example.com/p2.jpg",
                video_url="http://example.com/v2.mp4",
                category_id=category.id,
            )
            db.add_all([movie1, movie2])
            await db.commit()
            await db.refresh(movie1)
            await db.refresh(movie2)
            return movie1.id, movie2.id

    return asyncio.run(_create())
