from settings.django.base import MIDDLEWARE

session_middleware_index = MIDDLEWARE.index(
    "django.contrib.sessions.middleware.SessionMiddleware"
)

MIDDLEWARE.insert(
    session_middleware_index + 1, "django.middleware.locale.LocaleMiddleware"
)

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
