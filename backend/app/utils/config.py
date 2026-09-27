from functools import lru_cache
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        hide_input_in_errors=True,
    )

    app_name: str = "SolarSync API"
    upload_dir: Path = Path(__file__).resolve().parents[2] / "private_uploads"
    app_environment: Literal["development", "production", "test"] = "development"
    redis_url: str = "redis://127.0.0.1:6379/0"
    # Separate from the evictable response cache: security counters must survive it.
    auth_redis_url: str = "redis://127.0.0.1:6380/0"
    login_account_limit: int = Field(default=10, ge=1, le=100)
    login_account_window_seconds: int = Field(default=900, ge=60, le=3600)
    login_global_limit: int = Field(default=120, ge=1, le=10000)
    session_lifetime_seconds: int = Field(default=28800, ge=300, le=86400)
    session_idle_seconds: int = Field(default=1800, ge=120, le=28800)
    cache_enabled: bool = True
    metrics_enabled: bool = False
    cookie_secure: bool = False  # Set true behind HTTPS in production.
    db_host: str = "127.0.0.1"
    db_port: int = Field(default=3306, ge=1, le=65535)
    db_name: str = "solarsync"
    db_user: str = "solarsync_app"
    db_password: SecretStr
    cors_origins: list[str] = ["http://localhost:3000"]

    @model_validator(mode="after")
    def validate_auth_settings(self):
        if self.session_idle_seconds > self.session_lifetime_seconds:
            raise ValueError("SESSION_IDLE_SECONDS must not exceed SESSION_LIFETIME_SECONDS")
        if not self.cors_origins:
            raise ValueError("CORS_ORIGINS must contain exact frontend origins")
        for origin in self.cors_origins:
            parsed = urlsplit(origin)
            if (parsed.scheme not in ("http", "https") or not parsed.hostname
                    or parsed.username or parsed.password or parsed.path
                    or parsed.query or parsed.fragment or "*" in origin):
                raise ValueError("CORS_ORIGINS must contain exact HTTP(S) origins without paths")
            if self.app_environment == "production" and parsed.scheme != "https":
                raise ValueError("Production requires HTTPS in CORS_ORIGINS")
        if self.app_environment == "production":
            if not self.cookie_secure:
                raise ValueError("Production requires COOKIE_SECURE=true")
            cache, auth = urlsplit(self.redis_url), urlsplit(self.auth_redis_url)
            if (cache.hostname, cache.port or 6379) == (auth.hostname, auth.port or 6379):
                raise ValueError("AUTH_REDIS_URL must use a separate noeviction Redis server")
        return self

    @property
    def session_cookie_name(self) -> str:
        return "__Host-solarsync_session" if self.cookie_secure else "solarsync_session"

    @property
    def session_cookie_path(self) -> str:
        return "/" if self.cookie_secure else "/api/v1"

    @property
    def database_url(self) -> URL:
        # URL.create correctly handles @, %, / and other password characters.
        return URL.create(
            "mysql+pymysql", username=self.db_user,
            password=self.db_password.get_secret_value(), host=self.db_host,
            port=self.db_port, database=self.db_name,
            query={"charset": "utf8mb4"},
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
