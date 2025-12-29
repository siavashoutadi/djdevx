from settings.django.base import INSTALLED_APPS
from settings.utils.env import get_env

env = get_env()

ANYMAIL = {
    "BREVO_API_KEY": env("ANYMAIL_BREVO_API_KEY", default=""),
}

EMAIL_BACKEND = "anymail.backends.brevo.EmailBackend"

INSTALLED_APPS += [
    "anymail",
]

DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="")
SERVER_EMAIL = env("SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)
