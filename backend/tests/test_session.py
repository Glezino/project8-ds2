from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import session as session_module


def test_get_db_yields_and_closes_session() -> None:
    session_module.configure("sqlite://")

    gen = session_module.get_db()
    db = next(gen)
    try:
        assert isinstance(db, Session)
        db.execute(text("SELECT 1"))
        assert db.in_transaction()
    finally:
        try:
            next(gen)
        except StopIteration:
            pass

    assert not db.in_transaction()
