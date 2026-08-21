from settings.django.base import INSTALLED_APPS, MIDDLEWARE


INSTALLED_APPS += [
    "waffle",
]

MIDDLEWARE += [
    "waffle.middleware.WaffleMiddleware",
]
