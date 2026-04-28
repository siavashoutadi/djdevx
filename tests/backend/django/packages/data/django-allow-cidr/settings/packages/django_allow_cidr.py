from settings.django.base import MIDDLEWARE
from settings.utils.env import get_env

env = get_env()

MIDDLEWARE += [
    "allow_cidr.middleware.AllowCIDRMiddleware",
]

ALLOWED_CIDR_NETS = env("ALLOWED_CIDR_NETS", default=[])
