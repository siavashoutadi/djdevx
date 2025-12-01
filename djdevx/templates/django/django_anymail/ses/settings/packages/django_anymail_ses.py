from settings.utils.env import get_env

env = get_env()

ANYMAIL = {
    "AMAZON_SES_CLIENT_PARAMS": {
        "aws_access_key_id": env("ANYMAIL_SES_ACCESS_KEY", default=""),
        "aws_secret_access_key": env("ANYMAIL_SES_SECRET_KEY", default=""),
        "region_name": env("ANYMAIL_SES_REGION_NAME", default=""),
    }
}

EMAIL_BACKEND = "anymail.backends.amazon_ses.EmailBackend"

INSTALLED_APPS = [
    "anymail",
]
