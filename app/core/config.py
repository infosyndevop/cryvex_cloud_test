
import os
from typing import List, Union

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.constants import EnvironmentType


class Settings(BaseSettings):
    APP_NAME: str = "CRYVEX Cloud"
    APP_VERSION: str = "0.1.0"
    APP_ENV: EnvironmentType = Field(default="development")
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        """Normalize Render PostgreSQL URLs for async SQLAlchemy."""
        if not isinstance(value, str):
            return value

        value = value.strip()

        if value.startswith("postgresql://"):
            value = value.replace(
                "postgresql://",
                "postgresql+asyncpg://",
                1,
            )
        elif value.startswith("postgres://"):
            value = value.replace(
                "postgres://",
                "postgresql+asyncpg://",
                1,
            )

        return value

    # Security / JWT
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    CLOUD_JWT_AUDIENCE: str = "cryvex-cloud"

    # CORS
    CORS_ORIGINS: List[str] = []

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(
        cls, value: Union[str, List[str]]
    ) -> Union[List[str], str]:
        if isinstance(value, str) and not value.startswith("["):
            return [item.strip() for item in value.split(",") if item.strip()]
        elif isinstance(value, (list, str)):
            return value
        raise ValueError(value)

    # Logging
    LOG_LEVEL: str = "INFO"

    # Auth Defaults
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "100/minute"

    # Security
    TRUSTED_HOSTS: List[str] = ["*"]

    @field_validator("TRUSTED_HOSTS", mode="before")
    @classmethod
    def assemble_trusted_hosts(
        cls, value: Union[str, List[str]]
    ) -> Union[List[str], str]:
        if isinstance(value, str) and not value.startswith("["):
            return [item.strip() for item in value.split(",") if item.strip()]
        elif isinstance(value, (list, str)):
            return value
        raise ValueError(value)

    # ShopFlow Integration
    SHOPFLOW_BASE_URL: str = "http://localhost:8000"
    SHOPFLOW_SERVICE_TOKEN: str = ""
    SHOPFLOW_TIMEOUT_SECONDS: float = 30.0

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


def get_settings() -> Settings:
    settings = Settings()

    # Validation for production
    if settings.APP_ENV == "production":
        if settings.DEBUG:
            raise ValueError("DEBUG must be False in production")

        if not settings.CORS_ORIGINS or "*" in settings.CORS_ORIGINS:
            raise ValueError(
                "CORS_ORIGINS must be explicitly defined without wildcards "
                "in production"
            )

        if not settings.TRUSTED_HOSTS or "*" in settings.TRUSTED_HOSTS:
            raise ValueError(
                "TRUSTED_HOSTS must be explicitly defined without wildcards "
                "in production"
            )

    return settings


settings = get_settings()
