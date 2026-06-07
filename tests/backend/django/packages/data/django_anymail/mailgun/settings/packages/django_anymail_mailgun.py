from pydantic import SecretStr

from settings.django.base import INSTALLED_APPS
from settings.utils.base_settings import AppBaseSettings, IS_DEV

if not IS_DEV:

    class MailgunSettings(AppBaseSettings):
        anymail_mailgun_api_key: SecretStr
        anymail_mailgun_sender_domain: str

    _mailgun = MailgunSettings()

    ANYMAIL = {
        "MAILGUN_API_KEY": _mailgun.anymail_mailgun_api_key.get_secret_value(),
        "MAILGUN_API_URL": "https://api.mailgun.net/v3",
        "MAILGUN_SENDER_DOMAIN": _mailgun.anymail_mailgun_sender_domain,
    }

    EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"

    INSTALLED_APPS += [
        "anymail",
    ]
