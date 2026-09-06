"""OpenTelemetry server extension — activates tracing, metrics, and logs."""

from collections.abc import Callable
from typing import Any

from django.core.handlers.asgi import ASGIHandler

from otel.setup import setup_otel


def load(application: Callable[..., Any]) -> None:
    setup_otel()
    # DjangoInstrumentor activates by appending its middleware to
    # settings.MIDDLEWARE, but the handler built its middleware chain inside
    # get_wsgi_application()/get_asgi_application(), before this hook ran.
    # Rebuild the chain so request spans and server metrics are produced.
    application.load_middleware(is_async=isinstance(application, ASGIHandler))
