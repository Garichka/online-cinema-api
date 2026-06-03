import secrets
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from app.core.config import settings
from app.auth.router import router as auth_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend for the online cinema platform (FLEX level)",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.include_router(auth_router, prefix=settings.API_V1_STR)


security_basic = HTTPBasic()


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
            detail="Invalid documentation username or password.",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/docs", include_in_schema=False)
async def get_documentation(username: str = Depends(verify_docs_credentials)):
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{settings.PROJECT_NAME} - Swagger UI",
    )


@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint(username: str = Depends(verify_docs_credentials)):
    return get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=app.description,
        routes=app.routes,
    )


@app.get("/healthcheck", tags=["Health"])
async def health_check():
    return {"status": "healthy"}
