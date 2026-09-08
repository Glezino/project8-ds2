from fastapi import FastAPI

from app.config import Settings

settings = Settings()

app = FastAPI(debug=settings.debug)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
