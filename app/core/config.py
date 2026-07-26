from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path
from typing import Tuple
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"


class ConfigError(RuntimeError):
    """Raised when required runtime configuration is invalid."""


def _parse_admin_ids(raw_value: str | None) -> Tuple[int, ...]:
    if not raw_value:
        return tuple()

    ids: list[int] = []
    for item in raw_value.replace(";", ",").split(","):
        value = item.strip()
        if not value:
            continue
        try:
            ids.append(int(value))
        except ValueError as exc:
            raise ConfigError(f"ADMIN_IDS contains a non-integer value: {value!r}") from exc
    return tuple(ids)


def _parse_bool(raw_value: str | None, default: bool = False) -> bool:
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str
    bot_token: str
    database_url: str
    max_users: int
    timezone: str
    admin_ids: Tuple[int, ...]
    admin_username: str
    admin_password: str
    secret_key: str
    auto_create_db: bool
    log_level: str

    @property
    def timezone_info(self) -> ZoneInfo:
        try:
            return ZoneInfo(self.timezone)
        except ZoneInfoNotFoundError as exc:
            raise ConfigError(f"Invalid TIMEZONE value: {self.timezone!r}") from exc

    @property
    def async_database_url(self) -> str:
        url = self.database_url.strip()
        if url.startswith("sqlite:///"):
            return url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://", 1)
        return url

    def validate_bot_runtime(self) -> None:
        token = self.bot_token.strip()
        if not token or token == "replace-with-telegram-bot-token":
            raise ConfigError("BOT_TOKEN must be configured before starting the Telegram bot.")


def _read_int(name: str, default: int) -> int:
    raw_value = os.getenv(name, str(default))
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ConfigError(f"{name} must be an integer.") from exc
    if value < 1:
        raise ConfigError(f"{name} must be greater than zero.")
    return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    load_dotenv(ENV_FILE)

    return Settings(
        app_name=os.getenv("APP_NAME", "Challenge Omid"),
        bot_token=os.getenv("BOT_TOKEN", ""),
        database_url=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./challenge_omid.db"),
        max_users=_read_int("MAX_USERS", 400),
        timezone=os.getenv("TIMEZONE", "Asia/Tehran"),
        admin_ids=_parse_admin_ids(os.getenv("ADMIN_IDS")),
        admin_username=os.getenv("ADMIN_USERNAME", "admin"),
        admin_password=os.getenv("ADMIN_PASSWORD", ""),
        secret_key=os.getenv("SECRET_KEY", "change-me-to-a-long-random-secret"),
        auto_create_db=_parse_bool(os.getenv("AUTO_CREATE_DB"), default=True),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
