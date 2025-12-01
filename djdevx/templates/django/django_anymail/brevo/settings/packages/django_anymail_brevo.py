from settings.utils.env import get_env

env = get_env()

ANYMAIL = {
    "BREVO_API_KEY": env("ANYMAIL_BREVO_API_KEY", default=""),
}

EMAIL_BACKEND = "anymail.backends.brevo.EmailBackend"

INSTALLED_APPS = [
    "anymail",
]
