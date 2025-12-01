from settings.django.base import DEBUG
from settings.utils.env import get_env


env = get_env()

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
            "level": env("CONSOLE_LOG_LEVEL", default="INFO"),
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "filters": [],
        },
    },
    "loggers": {
        "django": {
            "level": env("DJANGO_LOG_LEVEL", default="WARNING"),
            "handlers": ["console"],
            "propagate": False,
        }
    },
    "root": {
        "level": env("ROOT_LOG_LEVEL", default="WARNING"),
        "handlers": ["console"],
    },
}

if DEBUG:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "require_debug_true": {
                "()": "django.utils.log.RequireDebugTrue",
            },
        },
        "formatters": {
            "rich": {"datefmt": "[%X]"},
        },
        "handlers": {
            "console": {
                "class": "rich.logging.RichHandler",
                "filters": ["require_debug_true"],
                "formatter": "rich",
                "level": "DEBUG",
                "rich_tracebacks": True,
                "tracebacks_show_locals": True,
            },
        },
        "loggers": {
            "django": {
                "handlers": [],
                "level": "INFO",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "INFO",
        },
    }
