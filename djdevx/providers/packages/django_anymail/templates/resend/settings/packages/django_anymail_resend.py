from pydantic import SecretStr

from settings.django.base import INSTALLED_APPS
from settings.utils.base_settings import AppBaseSettings, IS_DEV

if not IS_DEV:

    class _ResendSettings(AppBaseSettings):
        anymail_resend_api_key: SecretStr

    _resend = _ResendSettings()

    ANYMAIL = {
        "RESEND_API_KEY": _resend.anymail_resend_api_key.get_secret_value(),
    }

    EMAIL_BACKEND = "anymail.backends.resend.EmailBackend"

    INSTALLED_APPS += [
        "anymail",
    ]
