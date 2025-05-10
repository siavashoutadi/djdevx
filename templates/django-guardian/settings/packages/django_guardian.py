from settings import INSTALLED_APPS
from settings.django.auth import AUTHENTICATION_BACKENDS


INSTALLED_APPS += [
    "guardian",
]

AUTHENTICATION_BACKENDS += [
    "guardian.backends.ObjectPermissionBackend",
]
