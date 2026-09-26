"""URLs for the Sentry verification endpoint.

Mounted at the project root by ``urls/apps/sentry.py``, which only wires them
up when ``DEBUG`` is on.
"""

from django.urls import path

from sentry.views import trigger_error

urlpatterns = [
    path("sentry-debug/", trigger_error, name="sentry-debug"),
]
