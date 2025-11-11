from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_version: str = "1.0.0"
    environment: str = "development"
    default_timezone: str = "UTC"
    session_max_gap_seconds: int = 20
    session_max_duration_seconds: int = 120
    note_system_identifier: str = "Terranote Core v1.0"
    osm_api_base_url: str = "https://api.openstreetmap.org"
    osm_api_timeout_seconds: float = 10.0
    osm_max_retries: int = 2
    osm_retry_backoff_seconds: float = 0.2
    notifier_whatsapp_endpoint: str | None = None
    notifier_telegram_endpoint: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


