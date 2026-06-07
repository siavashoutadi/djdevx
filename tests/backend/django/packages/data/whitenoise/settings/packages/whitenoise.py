from settings.django.base import INSTALLED_APPS, MIDDLEWARE

INSTALLED_APPS.insert(0, "whitenoise.runserver_nostatic")

whitenoise_middleware = "whitenoise.middleware.WhiteNoiseMiddleware"

if whitenoise_middleware not in MIDDLEWARE:
    security_index = MIDDLEWARE.index("django.middleware.security.SecurityMiddleware")
    MIDDLEWARE.insert(security_index + 1, whitenoise_middleware)


STORAGES.update(  # noqa: F821
    {
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        }
    }
)
