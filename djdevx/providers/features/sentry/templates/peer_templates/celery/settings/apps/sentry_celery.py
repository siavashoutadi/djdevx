from typing import Any

from settings.utils.base_settings import AppBaseSettings


class SentryCelerySettings(AppBaseSettings):
    """Sentry options for Celery tasks.

    Copied into the project when the ``celery`` task queue is installed. The
    presence of the exported constants is what tells ``sentry.setup`` to
    register the Celery integration at all.

    ``SENTRY_CELERY_MONITOR_BEAT_TASKS`` is *not* declared here — it comes from
    the ``celery-beat`` peer so beat scheduling and task tracing stay
    independent concerns.
    """

    sentry_celery_propagate_traces: bool = True
    sentry_celery_exclude_beat_tasks: list[str] = []

    @classmethod
    def get_dev_defaults(cls) -> dict[str, Any]:
        return {"sentry_celery_propagate_traces": True}


_sentry_celery = SentryCelerySettings()

SENTRY_CELERY_PROPAGATE_TRACES: bool = _sentry_celery.sentry_celery_propagate_traces
SENTRY_CELERY_EXCLUDE_BEAT_TASKS: list[str] = (
    _sentry_celery.sentry_celery_exclude_beat_tasks
)
