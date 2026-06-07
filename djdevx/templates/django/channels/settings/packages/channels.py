from typing import Any

from pydantic import SecretStr

from settings.django.base import INSTALLED_APPS
from settings.utils.base_settings import AppBaseSettings


class ChannelsSettings(AppBaseSettings):
    redis_host: str
    redis_port: int = 6379
    redis_db: int = 1
    redis_password: SecretStr

    @classmethod
    def get_dev_defaults(cls) -> dict[str, Any]:
        return {
            "redis_host": "localhost",
            "redis_port": 6379,
            "username": "default",
            "redis_db": 1,
            "redis_password": "redis_password",
        }

    @classmethod
    def get_devcontainer_overrides(cls) -> dict[str, Any]:
        return {"redis_host": "cache"}


_channels = ChannelsSettings()

INSTALLED_APPS.insert(0, "daphne")
INSTALLED_APPS += [
    "channels",
]


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                {
                    "address": (
                        _channels.redis_host,
                        _channels.redis_port,
                    ),
                    "username": "default",
                    "password": _channels.redis_password.get_secret_value(),
                    "db": _channels.redis_db,
                }
            ],
        },
    },
}
