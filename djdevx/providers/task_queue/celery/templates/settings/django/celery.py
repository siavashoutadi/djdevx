from typing import Any
from urllib.parse import quote

from pydantic import SecretStr

from settings.utils.base_settings import AppBaseSettings


class CelerySettings(AppBaseSettings):
    """Celery broker/backend configuration.

    The native Redis dev cache publishes its port to ``.env.ddx`` as
    ``REDIS_PORT``, so ``redis_port`` picks it up in any process that loads
    these settings (workers, beat, the dev server). The broker/result URLs
    embed the redis password (dev default ``redis_password``): the native
    dev Redis instance and the ``cache`` compose service both require it, so
    a passwordless URL fails every broker/backend connection with an auth
    error.
    """

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: SecretStr | None = None
    celery_broker_url: str | None = None
    celery_result_backend: str | None = None
    celery_timezone: str = "UTC"
    celery_task_serializer: str = "json"

    @classmethod
    def get_dev_defaults(cls) -> dict[str, Any]:
        return {
            "redis_host": "localhost",
            "redis_port": 6379,
            "redis_password": "redis_password",
        }

    @classmethod
    def get_devcontainer_overrides(cls) -> dict[str, Any]:
        return {
            "redis_host": "cache",
            "celery_broker_url": "redis://:redis_password@cache:6379/0",
            "celery_result_backend": "redis://:redis_password@cache:6379/1",
        }


_celery = CelerySettings()

_redis_url = f"redis://{_celery.redis_host}:{_celery.redis_port}"
if _celery.redis_password is not None:
    _encoded_password = quote(_celery.redis_password.get_secret_value(), safe="")
    _redis_url = (
        f"redis://:{_encoded_password}@{_celery.redis_host}:{_celery.redis_port}"
    )

CELERY_BROKER_URL: str = _celery.celery_broker_url or f"{_redis_url}/0"
CELERY_RESULT_BACKEND: str = _celery.celery_result_backend or f"{_redis_url}/1"
CELERY_TIMEZONE: str = _celery.celery_timezone
CELERY_TASK_SERIALIZER: str = _celery.celery_task_serializer
