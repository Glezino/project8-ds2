from fastapi import FastAPI

from app.api.v1.router import router as v1_router
from app.config import Settings

settings = Settings()

app = FastAPI(debug=settings.debug)

app.include_router(v1_router, prefix="/api/v1")
