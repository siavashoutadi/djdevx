from settings.django.base import INSTALLED_APPS, MIDDLEWARE, DEBUG
from settings.django.auth import AUTHENTICATION_BACKENDS


INSTALLED_APPS += [
    "oauth2_provider",
]


AUTHENTICATION_BACKENDS += [
    "oauth2_provider.backends.OAuth2Backend",
]

oauth2_middleware = "oauth2_provider.middleware.OAuth2TokenMiddleware"

if oauth2_middleware not in MIDDLEWARE:
    try:
        index = MIDDLEWARE.index(
            "django.contrib.auth.middleware.AuthenticationMiddleware"
        )
        MIDDLEWARE.insert(index + 1, oauth2_middleware)
    except ValueError:
        MIDDLEWARE += ["oauth2_provider.middleware.OAuth2TokenMiddleware"]


OAUTH2_PROVIDER = {
    "ALLOWED_SCHEMES": ["http", "https"] if DEBUG else ["https"],
    "ALLOWED_REDIRECT_URI_SCHEMES": ["http", "https"] if DEBUG else ["https"],
}
