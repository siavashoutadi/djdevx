from django.apps import AppConfig


class OtelConfig(AppConfig):
    name = "otel"
    verbose_name = "OpenTelemetry"

    def ready(self) -> None:
        from otel.setup import setup_otel

        setup_otel()
