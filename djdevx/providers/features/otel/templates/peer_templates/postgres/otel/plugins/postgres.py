"""psycopg2 database instrumentation plugin.

Auto-discovered by ``otel.setup``. Tracks client query operations; it does not
provide PostgreSQL server metrics.
"""

import logging

from django.conf import settings

from otel.core import Providers

logger = logging.getLogger(__name__)


def instrument(providers: Providers) -> bool:
    if not getattr(settings, "OTEL_PSYCOPG2_ENABLED", True):
        return False

    try:
        from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
    except ImportError:
        logger.warning(
            "psycopg2 instrumentation unavailable: "
            "opentelemetry-instrumentation-psycopg2 is not installed"
        )
        return False

    kwargs = {}
    if getattr(settings, "OTEL_PSYCOPG2_ENABLE_COMMENTER", False):
        kwargs["enable_commenter"] = True
        kwargs["commenter_options"] = getattr(
            settings, "OTEL_PSYCOPG2_COMMENTER_OPTIONS", {}
        )

    Psycopg2Instrumentor().instrument(
        tracer_provider=providers.tracer_provider, **kwargs
    )
    return True
