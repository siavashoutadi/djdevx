from settings import INSTALLED_APPS, MIDDLEWARE


INSTALLED_APPS += [
    "auditlog",
]

MIDDLEWARE += [
    "auditlog.middleware.AuditlogMiddleware",
]
