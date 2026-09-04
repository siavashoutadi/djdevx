from settings.django.base import INSTALLED_APPS

INSTALLED_APPS += [
    "taggit",
]

TAGGIT_CASE_INSENSITIVE = False
TAGGIT_STRIP_UNICODE_WHEN_SLUGIFYING = False
