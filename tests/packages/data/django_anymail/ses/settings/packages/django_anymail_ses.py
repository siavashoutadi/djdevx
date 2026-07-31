from pydantic import SecretStr

from settings.django.base import INSTALLED_APPS
from settings.utils.base_settings import AppBaseSettings, IS_DEV

if not IS_DEV:

    class _SesSettings(AppBaseSettings):
        anymail_ses_access_key: SecretStr
        anymail_ses_secret_key: SecretStr
        anymail_ses_region_name: str

    _ses = _SesSettings()

    ANYMAIL = {
        "AMAZON_SES_CLIENT_PARAMS": {
            "aws_access_key_id": _ses.anymail_ses_access_key.get_secret_value(),
            "aws_secret_access_key": _ses.anymail_ses_secret_key.get_secret_value(),
            "region_name": _ses.anymail_ses_region_name,
        }
    }

    EMAIL_BACKEND = "anymail.backends.amazon_ses.EmailBackend"

    INSTALLED_APPS += [
        "anymail",
    ]
