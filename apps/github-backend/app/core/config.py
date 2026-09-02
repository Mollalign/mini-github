"""
Centralized application configuration.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["development", "staging", "production", "test"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = Field(
        default="Mini Github",
        alias="APP_NAME",
    )
    environment: Environment = Field(
        default="development",
        alias="ENVIRONMENT",
    )
    debug: bool = Field(
        default=False,
        alias="DEBUG",
    )
    api_v1_prefix: str = Field(
        default="/api/v1",
        alias="API_V1_PREFIX",
    )

    # Database
    database_url: str = Field(
        default="",
        alias="DATABASE_URL",
    )
    db_pool_size: int = Field(default=10, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=20, alias="DB_MAX_OVERFLOW")
    db_pool_timeout: int = Field(default=30, alias="DB_POOL_TIMEOUT")
    db_echo: bool = Field(default=False, alias="DB_ECHO")

    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        alias="REDIS_URL",
    )
    redis_max_connections: int = Field(
        default=50,
        alias="REDIS_MAX_CONNECTIONS",
    )

    # JWT
    jwt_secret_key: str = Field(
        default="",
        alias="JWT_SECRET_KEY",
    )
    jwt_algorithm: str = Field(
        default="HS256",
        alias="JWT_ALGORITHM",
    )
    jwt_access_token_expire_minutes: int = Field(
        default=60,
        alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
    )
    jwt_refresh_token_expire_days: int = Field(
        default=7,
        alias="JWT_REFRESH_TOKEN_EXPIRE_DAYS",
    )

    # Pagination
    default_page_size: int = Field(
        default=20,
        alias="DEFAULT_PAGE_SIZE",
    )
    max_page_size: int = Field(
        default=100,
        alias="MAX_PAGE_SIZE",
    )

    # Security
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"],
        alias="CORS_ORIGINS",
    )
    trusted_hosts: list[str] = Field(
        default_factory=lambda: ["*"],
        alias="TRUSTED_HOSTS",
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        alias="LOG_LEVEL",
    )
    log_json: bool = Field(
        default=False,
        alias="LOG_JSON",
    )

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        if self.environment == "production":
            if not self.database_url:
                raise ValueError("DATABASE_URL is required in production")

            if not self.jwt_secret_key:
                raise ValueError("JWT_SECRET_KEY is required in production")

            if self.debug:
                raise ValueError("DEBUG must be false in production")

        if self.max_page_size < self.default_page_size:
            raise ValueError(
                "MAX_PAGE_SIZE must be greater than or equal to DEFAULT_PAGE_SIZE"
            )

        if self.redis_max_connections <= 0:
            raise ValueError("REDIS_MAX_CONNECTIONS must be greater than 0")

        if self.jwt_access_token_expire_minutes <= 0:
            raise ValueError(
                "JWT_ACCESS_TOKEN_EXPIRE_MINUTES must be greater than 0"
            )

        if self.jwt_refresh_token_expire_days <= 0:
            raise ValueError(
                "JWT_REFRESH_TOKEN_EXPIRE_DAYS must be greater than 0"
            )

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()