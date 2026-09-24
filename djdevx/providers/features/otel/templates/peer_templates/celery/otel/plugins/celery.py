"""Celery worker instrumentation plugin.

Auto-discovered by ``otel.setup``. Can be turned off via
``OTEL_CELERY_ENABLED=False`` without deleting the plugin. Instruments task
execution (spans for task publish/run/retry) in both worker and Beat
processes; called from the generated ``applications/celery.py`` module before
any task runs.
"""

import logging

from django.conf import settings

from otel.core import Providers

logger = logging.getLogger(__name__)


def instrument(providers: Providers) -> bool:
    if not getattr(settings, "OTEL_CELERY_ENABLED", True):
        return False

    try:
        from opentelemetry.instrumentation.celery import CeleryInstrumentor
    except ImportError:
        logger.warning(
            "Celery instrumentation unavailable: "
            "opentelemetry-instrumentation-celery is not installed"
        )
        return False

    CeleryInstrumentor().instrument(tracer_provider=providers.tracer_provider)
    return True
