from typing import Any

from pydantic import SecretStr

from settings.utils.base_settings import AppBaseSettings


class CacheSettings(AppBaseSettings):
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
        return {
            "redis_host": "cache",
        }


_cache = CacheSettings()

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{_cache.redis_host}:{_cache.redis_port}/{_cache.redis_db}",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": _cache.redis_password.get_secret_value(),
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
            "IGNORE_EXCEPTIONS": True,
        },
    }
}

DJANGO_REDIS_LOG_IGNORED_EXCEPTIONS = True
