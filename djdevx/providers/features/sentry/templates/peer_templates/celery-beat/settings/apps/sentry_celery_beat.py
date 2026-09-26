from typing import Any

from settings.utils.base_settings import AppBaseSettings


class SentryCeleryBeatSettings(AppBaseSettings):
    """Sentry Crons options for Celery Beat.

    Copied into the project when the ``celery-beat`` scheduler is installed.
    With ``monitor_beat_tasks`` on, the SDK records monitor check-ins for the
    periodic tasks it finds, so a missed or slow schedule shows up in Sentry
    instead of silently disappearing.
    """

    sentry_celery_monitor_beat_tasks: bool = True

    @classmethod
    def get_dev_defaults(cls) -> dict[str, Any]:
        return {"sentry_celery_monitor_beat_tasks": True}


_sentry_celery_beat = SentryCeleryBeatSettings()

SENTRY_CELERY_MONITOR_BEAT_TASKS: bool = (
    _sentry_celery_beat.sentry_celery_monitor_beat_tasks
)
