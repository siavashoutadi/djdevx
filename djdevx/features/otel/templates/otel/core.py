"""Shared OpenTelemetry provider construction for trace, metrics, and logs."""

import atexit
import logging
from dataclasses import dataclass

from django.conf import settings

from opentelemetry import metrics, trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.logging.handler import LoggingHandler
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


@dataclass
class Providers:
    """The three registered providers plus the shared logging handler."""

    tracer_provider: TracerProvider
    meter_provider: MeterProvider
    logger_provider: LoggerProvider
    logging_handler: LoggingHandler


def build_providers() -> Providers:
    """Create, register, and return the shared OpenTelemetry providers.

    All three signals share one ``Resource`` with ``service.name`` taken from
    ``OTEL_SERVICE_NAME`` and export over OTLP/HTTP using the signal-specific
    ``OTEL_EXPORTER_OTLP_*_ENDPOINT`` settings.
    """
    resource = Resource.create({"service.name": settings.OTEL_SERVICE_NAME})

    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(endpoint=settings.OTEL_EXPORTER_OTLP_TRACES_ENDPOINT)
        )
    )
    trace.set_tracer_provider(tracer_provider)

    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[
            PeriodicExportingMetricReader(
                OTLPMetricExporter(
                    endpoint=settings.OTEL_EXPORTER_OTLP_METRICS_ENDPOINT
                )
            )
        ],
    )
    metrics.set_meter_provider(meter_provider)

    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(
            OTLPLogExporter(endpoint=settings.OTEL_EXPORTER_OTLP_LOGS_ENDPOINT)
        )
    )
    set_logger_provider(logger_provider)

    LoggingInstrumentor().instrument()
    logging_handler = next(
        h for h in logging.getLogger().handlers if isinstance(h, LoggingHandler)
    )

    def _shutdown() -> None:
        tracer_provider.shutdown()
        meter_provider.shutdown()
        logger_provider.force_flush()
        logger_provider.shutdown()

    atexit.register(_shutdown)

    return Providers(
        tracer_provider=tracer_provider,
        meter_provider=meter_provider,
        logger_provider=logger_provider,
        logging_handler=logging_handler,
    )
