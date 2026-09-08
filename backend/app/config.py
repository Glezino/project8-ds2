from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql://user:password@localhost:5432/dbname"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    ml_artifacts_path: Path = ROOT_DIR / "ml" / "artifacts"
