from pydantic import SecretStr

from settings.django.base import INSTALLED_APPS
from settings.utils.base_settings import AppBaseSettings, IS_DEV

if not IS_DEV:

    class MailjetSettings(AppBaseSettings):
        anymail_mailjet_api_key: SecretStr
        anymail_mailjet_secret_key: SecretStr

    _mailjet = MailjetSettings()

    ANYMAIL = {
        "MAILJET_API_KEY": _mailjet.anymail_mailjet_api_key.get_secret_value(),
        "MAILJET_SECRET_KEY": _mailjet.anymail_mailjet_secret_key.get_secret_value(),
    }

    EMAIL_BACKEND = "anymail.backends.mailjet.EmailBackend"

    INSTALLED_APPS += [
        "anymail",
    ]
