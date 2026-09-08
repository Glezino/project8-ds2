from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import Settings

settings = Settings()

_sessionmaker: sessionmaker | None = None


def configure(database_url: str | None = None) -> sessionmaker:
    """Create the engine and sessionmaker from a SQLAlchemy URL."""
    global _sessionmaker

    url = database_url or settings.database_url
    _sessionmaker = sessionmaker(bind=create_engine(url), autoflush=False, autocommit=False)
    return _sessionmaker


def get_sessionmaker() -> sessionmaker:
    if _sessionmaker is None:
        return configure()
    return _sessionmaker


def get_db() -> Generator[Session, None, None]:
    db = get_sessionmaker()()
    try:
        yield db
    finally:
        db.close()
