from settings.django.base import INSTALLED_APPS
from settings.utils.base_settings import AppBaseSettings
from pydantic import SecretStr


INSTALLED_APPS += [
    "allauth.idp.oidc",
]


class OIDCSettings(AppBaseSettings):
    idp_oidc_private_key: SecretStr


_oidc = OIDCSettings()

IDP_OIDC_PRIVATE_KEY = _oidc.idp_oidc_private_key
