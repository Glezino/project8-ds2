def test_get_db_dependency_importable() -> None:
    from app.api.deps import get_db

    assert callable(get_db)
