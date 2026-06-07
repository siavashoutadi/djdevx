from pydantic import SecretStr

from settings.django.base import INSTALLED_APPS
from settings.utils.base_settings import AppBaseSettings, IS_DEV


if not IS_DEV:

    class BrevoSettings(AppBaseSettings):
        anymail_brevo_api_key: SecretStr

    _brevo = BrevoSettings()

    ANYMAIL = {
        "BREVO_API_KEY": _brevo.anymail_brevo_api_key.get_secret_value(),
    }

    EMAIL_BACKEND = "anymail.backends.brevo.EmailBackend"

    INSTALLED_APPS += [
        "anymail",
    ]
