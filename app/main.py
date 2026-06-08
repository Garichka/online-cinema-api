import secrets
from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from app.core.config import settings

from app.auth.router import router as auth_router
from app.movies.router import router as movies_router
from app.reviews.router import router as reviews_router
from app.watchlist.router import router as watchlist_router
from app.payments.router import router as payments_router

security_basic = HTTPBasic()


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = redis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        encoding="utf8",
        decode_responses=False,
    )

    FastAPICache.init(
        RedisBackend(redis_client),
        prefix="cinema-cache",
    )

    print("🚀 Redis initialized")

    yield

    await redis_client.close()
    print("🛑 Redis closed")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend for the online cinema",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

# ======================
# ROUTERS
# ======================
app.include_router(auth_router)
app.include_router(movies_router)
app.include_router(reviews_router)
app.include_router(watchlist_router)
app.include_router(payments_router)


# ======================
# BASIC AUTH FOR DOCS
# ======================
def verify_docs_credentials(
    credentials: HTTPBasicCredentials = Depends(security_basic),
):
    correct_username = secrets.compare_digest(credentials.username, settings.DOCS_USER)
    correct_password = secrets.compare_digest(
        credentials.password, settings.DOCS_PASSWORD
    )

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid documentation credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username


# ======================
# DOCS
# ======================
@app.get("/docs", include_in_schema=False)
async def docs(username: str = Depends(verify_docs_credentials)):
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{settings.PROJECT_NAME} - Swagger UI",
    )


@app.get("/openapi.json", include_in_schema=False)
async def openapi(username: str = Depends(verify_docs_credentials)):
    return get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Backend for the online cinema",
        routes=app.routes,
    )


# ======================
# HEALTHCHECK
# ======================
@app.get("/healthcheck", tags=["Health"])
async def health_check():
    return {"status": "healthy"}
