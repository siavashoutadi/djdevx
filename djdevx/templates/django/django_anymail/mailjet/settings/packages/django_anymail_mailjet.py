from settings.django.base import INSTALLED_APPS, DEBUG
from settings.utils.env import get_env

env = get_env()

if not DEBUG:
    ANYMAIL = {
        "MAILJET_API_KEY": env("ANYMAIL_MAILJET_API_KEY", default=""),
        "MAILJET_SECRET_KEY": env("ANYMAIL_MAILJET_SECRET_KEY", default=""),
    }

    EMAIL_BACKEND = "anymail.backends.mailjet.EmailBackend"

    INSTALLED_APPS += [
        "anymail",
    ]

    DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="")
    SERVER_EMAIL = env("SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)
