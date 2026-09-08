from sqlalchemy import create_engine, inspect

from app.db.models import Base


def test_base_metadata_reflectable() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    inspector = inspect(engine)
    assert inspector.get_table_names() == []
