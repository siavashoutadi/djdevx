from settings.django.base import INSTALLED_APPS, MIDDLEWARE, DEBUG


if DEBUG:
    INSTALLED_APPS += [
        "django_browser_reload",
    ]

    MIDDLEWARE += [
        "django_browser_reload.middleware.BrowserReloadMiddleware",
    ]
