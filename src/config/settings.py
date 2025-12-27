import os
from pathlib import Path

from config.env_settings import env_settings


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env_settings.SECRET_KEY
DEBUG = env_settings.DEBUG

ALLOWED_HOSTS = env_settings.allowed_hosts_list()
CSRF_TRUSTED_ORIGINS = env_settings.csrf_trusted_origins_list()

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_crontab",
    "telegram_bot",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


if DEBUG:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env_settings.POSTGRES_DB,
            "USER": env_settings.POSTGRES_USER,
            "PASSWORD": env_settings.POSTGRES_PASSWORD,
            "HOST": env_settings.POSTGRES_HOST,
            "PORT": env_settings.POSTGRES_PORT,
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Cron задачи (оставлены пустыми, добавьте при необходимости)
CRONJOBS: list[tuple] = []


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "stdout_no_errors": {
            "()": "libs.logging.telegram_handler.MaxLevelFilter",
            "max_level": "WARNING",
        }
    },
    "formatters": {
        "console": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "telegram": {
            "format": "<b>[%(levelname)s]</b> %(name)s\\n%(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": env_settings.LOG_LEVEL,
            "filters": ["stdout_no_errors"],
            "formatter": "console",
        },
        "console_debug": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "console",
        },
        "telegram": {
            "class": "logging.NullHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console_debug" if DEBUG else "console"],
            "level": "DEBUG" if DEBUG else env_settings.LOG_LEVEL,
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console_debug" if DEBUG else "console"],
            "level": "ERROR",
            "propagate": False,
        },
        "jobs": {
            "handlers": ["console_debug" if DEBUG else "console", "telegram"],
            "level": "INFO",
            "propagate": False,
        },
        "access_requests": {
            "handlers": ["console_debug" if DEBUG else "console", "telegram"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console_debug" if DEBUG else "console", "telegram"],
        "level": "DEBUG" if DEBUG else env_settings.LOG_LEVEL,
    },
}

if env_settings.LOG_TELEGRAM_BOT_TOKEN and env_settings.LOG_TELEGRAM_CHAT_ID:
    LOGGING["handlers"]["telegram"] = {
        "level": "ERROR",
        "class": "libs.logging.telegram_handler.TelegramLoggingHandler",
        "bot_token": env_settings.LOG_TELEGRAM_BOT_TOKEN,
        "chat_id": env_settings.LOG_TELEGRAM_CHAT_ID,
        "service_name": env_settings.LOG_SERVICE_NAME,
        "formatter": "telegram",
    }
