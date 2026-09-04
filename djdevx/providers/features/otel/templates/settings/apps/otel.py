from typing import Any

from settings import PROJECT_NAME
from settings.django.base import INSTALLED_APPS
from settings.utils.base_settings import AppBaseSettings


def _default_otlp_endpoint() -> str:
    """Native pixi path: the collector port is pushed into OTEL_COLLECTOR_PORT."""
    return f"http://localhost:{__import__('os').environ.get('OTEL_COLLECTOR_PORT', '4318')}"


class OtelSettings(AppBaseSettings):
    otel_service_name: str = f"{PROJECT_NAME}-web"
    otel_exporter_otlp_endpoint: str
    otel_exporter_otlp_traces_endpoint: str | None = None
    otel_exporter_otlp_metrics_endpoint: str | None = None
    otel_exporter_otlp_logs_endpoint: str | None = None

    @classmethod
    def get_dev_defaults(cls) -> dict[str, Any]:
        return {
            "otel_exporter_otlp_endpoint": _default_otlp_endpoint(),
        }

    @classmethod
    def get_devcontainer_overrides(cls) -> dict[str, Any]:
        return {
            "otel_exporter_otlp_endpoint": "http://otlp:4318",
        }


_otel = OtelSettings()

OTEL_SERVICE_NAME: str = _otel.otel_service_name
OTEL_EXPORTER_OTLP_ENDPOINT: str = _otel.otel_exporter_otlp_endpoint

_otel_base = _otel.otel_exporter_otlp_endpoint.rstrip("/")
OTEL_EXPORTER_OTLP_TRACES_ENDPOINT: str = (
    _otel.otel_exporter_otlp_traces_endpoint or f"{_otel_base}/v1/traces"
)
OTEL_EXPORTER_OTLP_METRICS_ENDPOINT: str = (
    _otel.otel_exporter_otlp_metrics_endpoint or f"{_otel_base}/v1/metrics"
)
OTEL_EXPORTER_OTLP_LOGS_ENDPOINT: str = (
    _otel.otel_exporter_otlp_logs_endpoint or f"{_otel_base}/v1/logs"
)

INSTALLED_APPS += ["otel"]
