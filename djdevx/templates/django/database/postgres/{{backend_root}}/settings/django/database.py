from typing import Any

from pydantic import SecretStr

from settings.utils.base_settings import AppBaseSettings


class DatabaseSettings(AppBaseSettings):
    postgres_server: str
    postgres_port: int = 5432
    postgres_db: str
    postgres_user: str
    postgres_password: SecretStr

    @classmethod
    def get_dev_defaults(cls) -> dict[str, Any]:
        return {
            "postgres_server": "localhost",
            "postgres_port": 5432,
            "postgres_db": "postgres",
            "postgres_user": "postgres",
            "postgres_password": "devpassword",
        }

    @classmethod
    def get_devcontainer_overrides(cls) -> dict[str, Any]:
        return {"postgres_server": "db"}


_db = DatabaseSettings()

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": _db.postgres_server,
        "PORT": str(_db.postgres_port),
        "NAME": _db.postgres_db,
        "USER": _db.postgres_user,
        "PASSWORD": _db.postgres_password.get_secret_value(),
    }
}
