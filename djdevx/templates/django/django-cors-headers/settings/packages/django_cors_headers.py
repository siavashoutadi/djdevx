from settings.django.base import DEBUG, INSTALLED_APPS, MIDDLEWARE
from settings.utils.env import get_env


INSTALLED_APPS += [
    "corsheaders",
]

MIDDLEWARE.insert(0, "corsheaders.middleware.CorsMiddleware")

env = get_env()

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS", default=[])
    CORS_ALLOWED_ORIGIN_REGEXES = env("CORS_ALLOWED_ORIGIN_REGEXES", default=[])
