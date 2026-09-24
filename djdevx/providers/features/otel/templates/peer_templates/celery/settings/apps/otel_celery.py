from settings.utils.base_settings import AppBaseSettings


class OtelCelerySettings(AppBaseSettings):
    otel_celery_enabled: bool = True


_otel_celery = OtelCelerySettings()

OTEL_CELERY_ENABLED: bool = _otel_celery.otel_celery_enabled
