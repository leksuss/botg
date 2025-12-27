from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import AnyHttpUrl, BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent


class TelegramSettings(BaseModel):
    """Настройки Telegram-бота."""

    BOT_TOKEN: SecretStr
    """Токен Telegram-бота (BotFather)."""


class EnvSettings(BaseSettings):
    """Глобальные настройки проекта."""

    SECRET_KEY: str
    DEBUG: bool = False

    DJANGO_ALLOWED_HOSTS: str = ""
    DJANGO_CSRF_TRUSTED_ORIGINS: str = ""
    ADMIN_WHITELIST_IPS: Optional[str] = None

    TELEGRAM: TelegramSettings

    # Logging
    LOG_LEVEL: str = Field(default="INFO", alias="LOG_LEVEL")
    LOG_TELEGRAM_BOT_TOKEN: Optional[str] = None
    LOG_TELEGRAM_CHAT_ID: Optional[str] = None
    LOG_SERVICE_NAME: Optional[str] = None

    # Postgres (используется в проде)
    POSTGRES_DB: str = "postgres"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432

    # Внешние сервисы — пример базового URL, оставляем для расширения
    EXTERNAL_API_BASE_URL: Optional[AnyHttpUrl] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        validate_default=True,
        use_attribute_docstrings=True,
        extra="forbid",
    )

    def allowed_hosts_list(self) -> list[str]:
        raw = (self.DJANGO_ALLOWED_HOSTS or "").strip()
        return [h.strip() for h in raw.split(",") if h.strip()]

    def csrf_trusted_origins_list(self) -> list[str]:
        raw = (self.DJANGO_CSRF_TRUSTED_ORIGINS or "").strip()
        return [o.strip().rstrip("/") for o in raw.split(",") if o.strip()]

    def admin_whitelist_ips_list(self) -> list[str]:
        raw = (self.ADMIN_WHITELIST_IPS or "").strip()
        return [ip.strip() for ip in raw.replace(";", ",").split(",") if ip.strip()]


@lru_cache(maxsize=1)
def get_env_settings() -> EnvSettings:
    return EnvSettings()


env_settings = get_env_settings()
