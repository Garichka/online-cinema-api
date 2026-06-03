from fastapi import FastAPI
from app.core.config import settings
from app.auth.router import router as auth_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend for the online cinema",
    docs_url=None,
    redoc_url=None,
)

app.include_router(auth_router, prefix=settings.API_V1_STR)


@app.get("/healthcheck", tags=["Health"])
async def health_check():
    return {"status": "healthy"}
