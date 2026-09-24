from typing import Any

from settings.utils.base_settings import AppBaseSettings


class CelerySettings(AppBaseSettings):
    """Celery broker/backend configuration.

    The native Redis dev cache publishes its port to ``.env.ddx`` as
    ``REDIS_PORT``, so ``redis_port`` picks it up in any process that loads
    these settings (workers, beat, the dev server). In a devcontainer the
    broker/backend point at the ``cache`` compose service instead.
    """

    redis_port: int = 6379
    celery_broker_url: str | None = None
    celery_result_backend: str | None = None
    celery_timezone: str = "UTC"
    celery_task_serializer: str = "json"

    @classmethod
    def get_devcontainer_overrides(cls) -> dict[str, Any]:
        return {
            "celery_broker_url": "redis://cache:6379/0",
            "celery_result_backend": "redis://cache:6379/1",
        }


_celery = CelerySettings()

_redis = f"redis://127.0.0.1:{_celery.redis_port}"

CELERY_BROKER_URL: str = _celery.celery_broker_url or f"{_redis}/0"
CELERY_RESULT_BACKEND: str = _celery.celery_result_backend or f"{_redis}/1"
CELERY_TIMEZONE: str = _celery.celery_timezone
CELERY_TASK_SERIALIZER: str = _celery.celery_task_serializer
