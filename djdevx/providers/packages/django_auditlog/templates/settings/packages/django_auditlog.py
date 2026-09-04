from settings.django.base import INSTALLED_APPS, MIDDLEWARE


INSTALLED_APPS += [
    "auditlog",
]

MIDDLEWARE += [
    "auditlog.middleware.AuditlogMiddleware",
]
