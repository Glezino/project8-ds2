from sqlalchemy import text
from sqlalchemy.orm import Session


def test_get_db_yields_and_closes_session(db_session: Session) -> None:
    assert isinstance(db_session, Session)
    db_session.execute(text("SELECT 1"))
    assert db_session.in_transaction()
    db_session.close()
    assert not db_session.in_transaction()
