from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[str(BACKEND_DIR / ".env"), ".env"], extra="ignore"
    )
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash-lite"
    database_url: str = (
        "postgresql+asyncpg://nexus:nexus_secret@localhost:5432/nexus_db"
    )
    redis_url: str = "redis://localhost:6379/0"


settings = Settings()
