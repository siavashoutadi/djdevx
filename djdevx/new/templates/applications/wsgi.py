import os

from django.core.wsgi import get_wsgi_application

from applications import extensions

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

application = get_wsgi_application()

# Load server-only feature extensions (e.g. otel, channels); intentionally
# skipped by management commands.
extensions.load(application)
