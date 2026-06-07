from typing import Any

from pydantic import SecretStr

from settings import BASE_DIR
from settings.utils.base_settings import AppBaseSettings


class DjangoBaseSettings(AppBaseSettings):
    secret_key: SecretStr
    debug: bool
    allowed_hosts: list[str]
    csrf_trusted_origins: list[str]

    @classmethod
    def get_dev_defaults(cls) -> dict[str, Any]:
        return {
            "debug": True,
            "allowed_hosts": ["127.0.0.1", "localhost", "0.0.0.0"],
            "csrf_trusted_origins": [
                "http://localhost:8000",
                "https://localhost:8000",
                "http://127.0.0.1:8000",
                "https://127.0.0.1:8000",
                "http://0.0.0.0:8000",
                "https://0.0.0.0:8000",
                "http://localhost:3000",
                "https://localhost:3000",
                "http://127.0.0.1:3000",
                "https://127.0.0.1:3000",
                "http://0.0.0.0:3000",
                "https://0.0.0.0:3000",
                "http://localhost:4200",
                "https://localhost:4200",
                "http://127.0.0.1:4200",
                "https://127.0.0.1:4200",
                "http://0.0.0.0:4200",
                "https://0.0.0.0:4200",
                "http://localhost:5173",
                "https://localhost:5173",
                "http://127.0.0.1:5173",
                "https://127.0.0.1:5173",
                "http://0.0.0.0:5173",
                "https://0.0.0.0:5173",
            ],
        }


_base = DjangoBaseSettings()

SECRET_KEY: str = _base.secret_key.get_secret_value()
DEBUG: bool = _base.debug
ALLOWED_HOSTS: list[str] = _base.allowed_hosts
CSRF_TRUSTED_ORIGINS: list[str] = _base.csrf_trusted_origins

DEFAULT_AUTO_FIELD: str = "django.db.models.BigAutoField"
ROOT_URLCONF: str = "urls"
WSGI_APPLICATION: str = "applications.wsgi.application"
ASGI_APPLICATION: str = "applications.asgi.application"

INSTALLED_APPS: list[str] = [
    "users.apps.UsersConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE: list[str] = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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
