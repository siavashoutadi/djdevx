from settings.django.base import INSTALLED_APPS, MIDDLEWARE
from settings.utils.base_settings import AppBaseSettings, IS_DEV

INSTALLED_APPS += [
    "corsheaders",
]

MIDDLEWARE.insert(0, "corsheaders.middleware.CorsMiddleware")

if IS_DEV:
    CORS_ALLOW_ALL_ORIGINS = True
else:

    class CorsSettings(AppBaseSettings):
        cors_allowed_origins: list[str]
        cors_allowed_origin_regexes: list[str]

    _cors = CorsSettings()
    CORS_ALLOWED_ORIGINS = _cors.cors_allowed_origins
    CORS_ALLOWED_ORIGIN_REGEXES = _cors.cors_allowed_origin_regexes
