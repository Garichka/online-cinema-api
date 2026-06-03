from fastapi import FastAPI

app = FastAPI(title="Online Cinema API", version="0.1.0", docs_url=None, redoc_url=None)


@app.get("/healthcheck", tags=["Health"])
async def health_check():
    return {"status": "healthy"}
