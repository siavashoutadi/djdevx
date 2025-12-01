from settings.utils.env import get_env

env = get_env()

ANYMAIL = {
    "RESEND_API_KEY": env("ANYMAIL_RESEND_API_KEY", default=""),
}

EMAIL_BACKEND = "anymail.backends.resend.EmailBackend"

INSTALLED_APPS = [
    "anymail",
]
