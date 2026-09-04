"""OpenTelemetry orchestration — the single entry point for otel setup.

``setup_otel`` builds the shared providers, instruments the Django framework,
discovers and runs instrumentation plugins from ``otel.plugins``, and guards
against running twice in the same interpreter process.
"""

import importlib
import logging
import pkgutil

import otel.plugins as plugins
from opentelemetry.instrumentation.django import DjangoInstrumentor

from .core import build_providers

logger = logging.getLogger(__name__)

_SETUP_COMPLETE = False


def setup_otel() -> None:
    global _SETUP_COMPLETE

    if _SETUP_COMPLETE:
        return

    providers = build_providers()

    DjangoInstrumentor().instrument(
        tracer_provider=providers.tracer_provider,
        meter_provider=providers.meter_provider,
    )

    for module_info in pkgutil.iter_modules(plugins.__path__):
        if module_info.name.startswith("_"):
            continue

        module_name = f"{plugins.__name__}.{module_info.name}"
        try:
            plugin = importlib.import_module(module_name)
        except ImportError as exc:
            logger.warning(
                "otel plugin %r skipped: could not import (%s)", module_info.name, exc
            )
            continue

        instrument = getattr(plugin, "instrument", None)
        if not callable(instrument):
            logger.warning("otel plugin %r has no instrument()", module_info.name)
            continue

        try:
            activated = instrument(providers)
        except ImportError as exc:
            logger.warning(
                "otel plugin %r skipped: optional dependency missing (%s)",
                module_info.name,
                exc,
            )
            continue

        if activated:
            logger.info("Enabled otel plugin %r", module_info.name)
        else:
            logger.info("Skipped otel plugin %r (disabled)", module_info.name)

    _SETUP_COMPLETE = True
