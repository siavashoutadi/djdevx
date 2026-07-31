import sys

from settings.django.base import INSTALLED_APPS, MIDDLEWARE

TESTING = "test" in sys.argv

if not TESTING:
    INSTALLED_APPS += [
        "silk",
    ]

    MIDDLEWARE += [
        "silk.middleware.SilkyMiddleware",
    ]

    # Configure Silk profiling
    SILKY_PYTHON_PROFILER = False
    SILKY_AUTHENTICATION = False
    SILKY_AUTHORISATION = False
    SILKY_INTERCEPT_PERCENT = 100
    SILKY_MAX_REQUEST_BODY_SIZE = -1
    SILKY_MAX_RESPONSE_BODY_SIZE = -1
    SILKY_META = False
