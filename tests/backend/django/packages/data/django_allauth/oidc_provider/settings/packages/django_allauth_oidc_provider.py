from settings import INSTALLED_APPS
from settings.utils.env import get_env

INSTALLED_APPS += [
    "allauth.idp.oidc",
]

env = get_env()

# Private key for signing ID tokens - REQUIRED
IDP_OIDC_PRIVATE_KEY = env("IDP_OIDC_PRIVATE_KEY", default="")
