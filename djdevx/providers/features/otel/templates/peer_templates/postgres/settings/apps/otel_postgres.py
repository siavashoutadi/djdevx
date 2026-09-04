from typing import Any

from settings.utils.base_settings import AppBaseSettings


class OtelPostgresSettings(AppBaseSettings):
    otel_psycopg2_enabled: bool = True
    otel_psycopg2_enable_commenter: bool = False
    otel_psycopg2_commenter_options: dict[str, Any] = {}


_otel_postgres = OtelPostgresSettings()

OTEL_PSYCOPG2_ENABLED: bool = _otel_postgres.otel_psycopg2_enabled
OTEL_PSYCOPG2_ENABLE_COMMENTER: bool = _otel_postgres.otel_psycopg2_enable_commenter
OTEL_PSYCOPG2_COMMENTER_OPTIONS: dict[str, Any] = (
    _otel_postgres.otel_psycopg2_commenter_options
)
