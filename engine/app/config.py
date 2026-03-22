from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/appdb"
    redis_url: str = "redis://redis:6379/0"
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    debug: bool = False
    log_level: str = "INFO"
    app_name: str = "Engine API"
    app_version: str = "0.1.0"


@lru_cache
def get_settings() -> Settings:
    return Settings()
