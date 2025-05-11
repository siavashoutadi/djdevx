from settings import INSTALLED_APPS, MIDDLEWARE
from csp.constants import NONE, SELF


INSTALLED_APPS += [
    "csp",
]

MIDDLEWARE += [
    "csp.middleware.CSPMiddleware",
]

CONTENT_SECURITY_POLICY = {
    "EXCLUDE_URL_PREFIXES": ["/excluded-path/"],
    "DIRECTIVES": {
        "default-src": [SELF, "cdn.example.net"],
        "frame-ancestors": [SELF],
        "form-action": [SELF],
        "report-uri": "/csp-report/",
    },
}

CONTENT_SECURITY_POLICY_REPORT_ONLY = {
    "EXCLUDE_URL_PREFIXES": ["/excluded-path/"],
    "DIRECTIVES": {
        "default-src": [NONE],
        "connect-src": [SELF],
        "img-src": [SELF],
        "form-action": [SELF],
        "frame-ancestors": [SELF],
        "script-src": [SELF],
        "style-src": [SELF],
        "upgrade-insecure-requests": True,
        "report-uri": "/csp-report/",
    },
}
