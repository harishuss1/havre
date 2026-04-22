"""
config.py — App settings loaded from environment variables.
All config is read from .env via pydantic-settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    database_url: str = "postgresql+psycopg://havre:havre_dev_password@localhost:5432/havre"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Notifications
    resend_api_key: str = ""
    notification_email: str = ""

    # API
    api_key: str = "havre_local_dev_key"

    # App
    environment: str = "development"

    @property
    def is_dev(self) -> bool:
        return self.environment == "development"


# Single shared instance used everywhere
settings = Settings()