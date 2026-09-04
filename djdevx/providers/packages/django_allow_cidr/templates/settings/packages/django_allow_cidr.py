from typing import Any

from settings.django.base import MIDDLEWARE
from settings.utils.base_settings import AppBaseSettings


class AllowCIDRSettings(AppBaseSettings):
    allowed_cidr_nets: list[str]

    @classmethod
    def get_dev_defaults(cls) -> dict[str, Any]:
        return {"allowed_cidr_nets": ["0.0.0.0/0", "::0/0"]}


_cidr = AllowCIDRSettings()

MIDDLEWARE += [
    "allow_cidr.middleware.AllowCIDRMiddleware",
]

ALLOWED_CIDR_NETS = _cidr.allowed_cidr_nets
