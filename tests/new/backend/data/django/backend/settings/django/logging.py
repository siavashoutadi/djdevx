from typing import Any

from settings.utils.base_settings import AppBaseSettings


class LoggingSettings(AppBaseSettings):
    use_rich_logging: bool = False
    console_log_level: str = "INFO"
    django_log_level: str = "WARNING"
    root_log_level: str = "WARNING"

    @classmethod
    def get_dev_defaults(cls) -> dict[str, Any]:
        return {
            "use_rich_logging": True,
            "console_log_level": "DEBUG",
            "django_log_level": "INFO",
            "root_log_level": "INFO",
        }


_log = LoggingSettings()

if _log.use_rich_logging:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "rich": {"datefmt": "[%X]"},
        },
        "handlers": {
            "console": {
                "class": "rich.logging.RichHandler",
                "formatter": "rich",
                "level": _log.console_log_level,
                "rich_tracebacks": True,
                "tracebacks_show_locals": True,
            },
        },
        "loggers": {
            "django": {
                "handlers": [],
                "level": _log.django_log_level,
            },
        },
        "root": {
            "handlers": ["console"],
            "level": _log.root_log_level,
        },
    }
else:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            },
        },
        "handlers": {
            "console": {
                "level": _log.console_log_level,
                "class": "logging.StreamHandler",
                "formatter": "standard",
            },
        },
        "loggers": {
            "django": {
                "level": _log.django_log_level,
                "handlers": ["console"],
                "propagate": False,
            },
        },
        "root": {
            "level": _log.root_log_level,
            "handlers": ["console"],
        },
    }
