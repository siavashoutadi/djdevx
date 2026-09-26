from django.urls import include, path

from settings.django.base import DEBUG

# The endpoint raises a ZeroDivisionError on purpose, so it is only wired up
# when DEBUG is on. With DEBUG off, ``sentry-debug/`` 404s like any other
# unknown path.
urlpatterns = [path("", include("sentry.urls"))] if DEBUG else []
