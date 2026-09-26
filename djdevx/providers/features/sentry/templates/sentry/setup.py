"""Sentry SDK bootstrap — the single entry point for Sentry setup.

``setup_sentry`` translates the ``SENTRY_*`` Django settings into
``sentry_sdk.init()`` options. It runs once per process, is idempotent, and
never raises: monitoring must not be able to break the application.

Integrations configured here:

* ``DjangoIntegration`` — request/exception/signal instrumentation.
* ``LoggingIntegration`` — structured log shipping.
* ``CeleryIntegration`` — added only when the Celery peer settings are present
  (i.e. the ``celery`` task queue is installed).

Celery Beat's ``monitor_beat_tasks`` (Sentry Crons) comes from the
``celery-beat`` peer settings and is read with ``getattr`` so the same
generated code works with or without that peer.
"""

import logging
from typing import Any

import sentry_sdk
from django.conf import settings
from sentry_sdk.integrations import DidNotEnable
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

logger = logging.getLogger(__name__)

_INITIALIZED = False


def setup_sentry() -> None:
    """Initialize the Sentry SDK once per process. No-op without a DSN."""
    global _INITIALIZED

    if _INITIALIZED:
        return

    dsn = getattr(settings, "SENTRY_DSN", "")
    if not dsn:
        logger.debug("Sentry is disabled: no SENTRY_DSN configured")
        return

    try:
        sentry_sdk.init(**_build_options(dsn))
    except Exception:
        logger.exception("Sentry SDK initialization failed; monitoring is off")
        return

    _INITIALIZED = True


def _build_options(dsn: str) -> dict[str, Any]:
    """Map Django settings onto ``sentry_sdk.init()`` options."""
    options: dict[str, Any] = {
        "dsn": dsn,
        "environment": settings.SENTRY_ENVIRONMENT or None,
        "release": settings.SENTRY_RELEASE or None,
        "sample_rate": settings.SENTRY_SAMPLE_RATE,
        "traces_sample_rate": settings.SENTRY_TRACES_SAMPLE_RATE,
        "profiles_sample_rate": settings.SENTRY_PROFILES_SAMPLE_RATE,
        "profile_lifecycle": settings.SENTRY_PROFILE_LIFECYCLE,
        "send_default_pii": settings.SENTRY_SEND_DEFAULT_PII,
        "max_breadcrumbs": settings.SENTRY_MAX_BREADCRUMBS,
        "max_request_body_size": settings.SENTRY_MAX_REQUEST_BODY_SIZE,
        "attach_stacktrace": settings.SENTRY_ATTACH_STACKTRACE,
        "include_local_variables": settings.SENTRY_INCLUDE_LOCAL_VARIABLES,
        "debug": settings.SENTRY_DEBUG,
        "integrations": [
            DjangoIntegration(
                middleware_spans=settings.SENTRY_MIDDLEWARE_SPANS,
                signals_spans=settings.SENTRY_SIGNALS_SPANS,
                cache_spans=settings.SENTRY_CACHE_SPANS,
                http_methods_to_capture=tuple(settings.SENTRY_HTTP_METHODS_TO_CAPTURE),
            ),
            LoggingIntegration(
                capture_sentry_logs=settings.SENTRY_CAPTURE_LOGS,
                sentry_logs_level=settings.SENTRY_LOGS_LEVEL,
                level=settings.SENTRY_BREADCRUMB_LEVEL,
                event_level=settings.SENTRY_EVENT_LEVEL,
            ),
        ],
    }

    celery_integration = _celery_integration()
    if celery_integration is not None:
        options["integrations"].append(celery_integration)

    return options


def _celery_integration() -> Any:
    """Return a ``CeleryIntegration`` when the Celery peer settings exist.

    Presence of the exported ``SENTRY_CELERY_*`` constants is the signal that
    ``ddx task-queue add celery`` is in effect: Celery is not in
    ``INSTALLED_APPS`` here, so there is nothing to introspect.
    """
    if not hasattr(settings, "SENTRY_CELERY_PROPAGATE_TRACES"):
        return None

    try:
        from sentry_sdk.integrations.celery import CeleryIntegration
    except ImportError, DidNotEnable:
        # ``DidNotEnable`` is what the SDK raises when its celery integration
        # imports but Celery itself is missing. It is not an ImportError.
        logger.warning(
            "Sentry Celery integration unavailable; task errors will still be "
            "reported but task traces and check-ins will not"
        )
        return None

    exclude_beat_tasks = list(getattr(settings, "SENTRY_CELERY_EXCLUDE_BEAT_TASKS", ()))
    return CeleryIntegration(
        propagate_traces=settings.SENTRY_CELERY_PROPAGATE_TRACES,
        monitor_beat_tasks=getattr(settings, "SENTRY_CELERY_MONITOR_BEAT_TASKS", False),
        exclude_beat_tasks=exclude_beat_tasks or None,
    )
