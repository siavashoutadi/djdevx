import sys

from settings.django.base import INSTALLED_APPS, MIDDLEWARE, DEBUG


if DEBUG:
    TESTING = "test" in sys.argv

    if not TESTING:
        INSTALLED_APPS += [
            "debug_toolbar",
        ]

        MIDDLEWARE += [
            "debug_toolbar.middleware.DebugToolbarMiddleware",
        ]

        INTERNAL_IPS = ["127.0.0.1", "localhost"]
