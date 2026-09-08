from pathlib import Path

from app.config import ROOT_DIR, Settings


def test_settings_defaults():
    settings = Settings(_env_file=None)
    assert settings.database_url.startswith("postgresql://")
    assert settings.api_host == "0.0.0.0"
    assert settings.api_port == 8000
    assert settings.debug is True


def test_ml_artifacts_path_default():
    settings = Settings(_env_file=None)
    assert settings.ml_artifacts_path == ROOT_DIR / "ml" / "artifacts"


def test_ml_artifacts_path_from_env(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        f"ML_ARTIFACTS_PATH={tmp_path / 'models'}\n",
        encoding="utf-8",
    )
    settings = Settings(_env_file=env_file)
    assert settings.ml_artifacts_path == tmp_path / "models"


def test_settings_load_from_env_file(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "DATABASE_URL=postgresql://test:test@localhost:5432/testdb\n"
        "API_HOST=127.0.0.1\n"
        "API_PORT=9000\n"
        "DEBUG=false\n",
        encoding="utf-8",
    )
    settings = Settings(_env_file=env_file)
    assert settings.database_url == "postgresql://test:test@localhost:5432/testdb"
    assert settings.api_host == "127.0.0.1"
    assert settings.api_port == 9000
    assert settings.debug is False


def test_env_file_points_to_repo_root():
    assert ROOT_DIR.name == "project8-ds2"
    assert (ROOT_DIR / ".env.example").exists()
