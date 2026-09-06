import os

from django.core.asgi import get_asgi_application

from applications import extensions

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

application = get_asgi_application()

# Load server-only feature extensions (e.g. otel, channels); intentionally
# skipped by management commands.
extensions.load(application)
