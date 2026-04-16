from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # api/


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    secret_key: str = "dev-insecure-change-me"
    registration_secret_key: str | None = None
    debug: bool = False

    database_url: str = f"sqlite:///{BASE_DIR}/db.sqlite3"

    access_token_lifetime_minutes: int = 60
    refresh_token_lifetime_days: int = 7

    magic_link_base_url: str = "http://localhost:5173"
    magic_link_expiry_minutes: int = 15

    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = "noreply@renovaite.com"
    mail_port: int = 587
    mail_server: str = "localhost"
    mail_use_tls: bool = True
    mail_console: bool = False  # if True, print emails to stdout instead of sending

    allowed_hosts: list[str] = ["localhost", "127.0.0.1"]

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "production", "prod"}:
                return False
            if normalized in {"development", "dev"}:
                return True
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
