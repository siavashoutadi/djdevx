import logging
from typing import Any, Literal

from pydantic import SecretStr

from settings.django.base import INSTALLED_APPS
from settings.utils.base_settings import AppBaseSettings


class SentrySettings(AppBaseSettings):
    """Sentry SDK configuration.

    ``sentry_dsn`` is deliberately required with no default: a placeholder DSN
    would silently drop events. Run ``ddx settings secrets init dev`` (or
    ``init prod``) to supply it.

    Field names deliberately mirror Sentry's native environment variables
    (``SENTRY_DSN``, ``SENTRY_ENVIRONMENT``, ``SENTRY_RELEASE``,
    ``SENTRY_DEBUG``) so container and cluster deployments can use either.
    """

    sentry_dsn: SecretStr
    # Core options
    sentry_environment: str = ""
    sentry_release: str = ""
    sentry_sample_rate: float = 1.0
    sentry_traces_sample_rate: float = 0.0
    sentry_profiles_sample_rate: float = 0.0
    sentry_profile_lifecycle: Literal["manual", "trace"] = "trace"
    sentry_send_default_pii: bool = False
    sentry_max_breadcrumbs: int = 100
    sentry_max_request_body_size: Literal["never", "small", "medium", "always"] = (
        "medium"
    )
    sentry_attach_stacktrace: bool = False
    sentry_include_local_variables: bool = True
    sentry_debug: bool = False
    # Django integration options
    sentry_middleware_spans: bool = False
    sentry_cache_spans: bool = False
    sentry_signals_spans: bool = True
    sentry_http_methods_to_capture: list[str] = [
        "CONNECT",
        "DELETE",
        "GET",
        "HEAD",
        "OPTIONS",
        "PATCH",
        "POST",
        "PUT",
        "TRACE",
    ]
    # Logging integration options. The three levels mirror the SDK's own
    # defaults, spelled as logging constants so they read clearly and can be
    # tuned per environment without touching generated code.
    sentry_capture_logs: bool = False
    sentry_logs_level: int = logging.INFO
    sentry_breadcrumb_level: int = logging.INFO
    sentry_event_level: int = logging.ERROR

    @classmethod
    def get_dev_defaults(cls) -> dict[str, Any]:
        return {
            "sentry_environment": "development",
            # Trace everything locally so performance issues are visible
            # without waiting for production sampling.
            "sentry_traces_sample_rate": 1.0,
            # Log shipping is on in dev to exercise the pipeline; production
            # keeps it off by default because it is noisy and costly.
            "sentry_capture_logs": True,
        }


_sentry = SentrySettings()

SENTRY_DSN: str = _sentry.sentry_dsn.get_secret_value()
SENTRY_ENVIRONMENT: str = _sentry.sentry_environment
SENTRY_RELEASE: str = _sentry.sentry_release
SENTRY_SAMPLE_RATE: float = _sentry.sentry_sample_rate
SENTRY_TRACES_SAMPLE_RATE: float = _sentry.sentry_traces_sample_rate
SENTRY_PROFILES_SAMPLE_RATE: float = _sentry.sentry_profiles_sample_rate
SENTRY_PROFILE_LIFECYCLE: str = _sentry.sentry_profile_lifecycle
SENTRY_SEND_DEFAULT_PII: bool = _sentry.sentry_send_default_pii
SENTRY_MAX_BREADCRUMBS: int = _sentry.sentry_max_breadcrumbs
SENTRY_MAX_REQUEST_BODY_SIZE: str = _sentry.sentry_max_request_body_size
SENTRY_ATTACH_STACKTRACE: bool = _sentry.sentry_attach_stacktrace
SENTRY_INCLUDE_LOCAL_VARIABLES: bool = _sentry.sentry_include_local_variables
SENTRY_DEBUG: bool = _sentry.sentry_debug
SENTRY_MIDDLEWARE_SPANS: bool = _sentry.sentry_middleware_spans
SENTRY_CACHE_SPANS: bool = _sentry.sentry_cache_spans
SENTRY_SIGNALS_SPANS: bool = _sentry.sentry_signals_spans
SENTRY_HTTP_METHODS_TO_CAPTURE: list[str] = _sentry.sentry_http_methods_to_capture
SENTRY_CAPTURE_LOGS: bool = _sentry.sentry_capture_logs
SENTRY_LOGS_LEVEL: int = _sentry.sentry_logs_level
SENTRY_BREADCRUMB_LEVEL: int = _sentry.sentry_breadcrumb_level
SENTRY_EVENT_LEVEL: int = _sentry.sentry_event_level

INSTALLED_APPS += ["sentry"]
