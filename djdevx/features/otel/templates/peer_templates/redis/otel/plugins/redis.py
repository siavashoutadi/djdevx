"""Redis client instrumentation plugin.

Auto-discovered by ``otel.setup``. Can be turned off via
``OTEL_REDIS_ENABLED=False`` without deleting the plugin. Tracks client
operations only; it does not provide Redis server metrics. No request/response
hooks are registered because they could capture command arguments.
"""

import logging

from django.conf import settings

from otel.core import Providers

logger = logging.getLogger(__name__)


def instrument(providers: Providers) -> bool:
    if not getattr(settings, "OTEL_REDIS_ENABLED", True):
        return False

    try:
        from opentelemetry.instrumentation.redis import RedisInstrumentor
    except ImportError:
        logger.warning(
            "Redis instrumentation unavailable: "
            "opentelemetry-instrumentation-redis is not installed"
        )
        return False

    RedisInstrumentor().instrument(tracer_provider=providers.tracer_provider)
    return True
