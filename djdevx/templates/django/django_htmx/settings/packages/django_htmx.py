from settings.django.base import INSTALLED_APPS, MIDDLEWARE


INSTALLED_APPS += [
    "django_htmx",
]

MIDDLEWARE += [
    "django_htmx.middleware.HtmxMiddleware",
]
