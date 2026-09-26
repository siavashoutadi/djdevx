"""Sentry app config — SDK bootstrap for every process.

``ready()`` is the right hook here: it runs exactly once per process, for the
web server, Celery workers, Celery Beat, and management commands alike.
Sentry's own guidance is that ``sentry_sdk.init()`` must happen on worker
startup and not only in the module where tasks are defined — the Celery
worker populates the Django app registry before executing any task, so
``ready()`` satisfies that requirement without touching the Celery app module.

``setup_sentry()`` is idempotent and never raises, so a misconfigured or
unreachable Sentry can't take the app registry (and therefore the whole
project) down.

The package is named ``sentry`` but nothing installed is: the SDK's import
name is ``sentry_sdk``, so this directory shadows no third-party module.
"""

from django.apps import AppConfig


class SentryConfig(AppConfig):
    name = "sentry"
    verbose_name = "Sentry"

    def ready(self) -> None:
        from sentry.setup import setup_sentry

        setup_sentry()
