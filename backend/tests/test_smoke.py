import importlib

import pytest

BACKEND_PACKAGES = [
    "fastapi",
    "uvicorn",
    "pydantic",
    "pydantic_settings",
    "sqlalchemy",
    "alembic",
]

ML_PACKAGES = [
    "polars",
    "sklearn",
    "xgboost",
    "optuna",
    "seaborn",
    "matplotlib",
]


@pytest.mark.parametrize("package", BACKEND_PACKAGES + ML_PACKAGES)
def test_package_importable(package: str) -> None:
    module = importlib.import_module(package)
    version = getattr(module, "__version__", None)
    assert version is not None, f"{package} does not expose __version__"
    assert isinstance(version, str) and version
