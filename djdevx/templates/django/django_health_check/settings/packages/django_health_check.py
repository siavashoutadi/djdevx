from typing import Any

from settings.django.base import INSTALLED_APPS
from settings.utils.base_settings import AppBaseSettings


class HealthCheckSettings(AppBaseSettings):
    health_check_url: str

    @classmethod
    def get_dev_defaults(cls) -> dict[str, Any]:
        return {"health_check_url": "hc"}


_hc = HealthCheckSettings()

INSTALLED_APPS += [
    "health_check",
]

HEALTH_CHECK_URL = _hc.health_check_url

HEALTH_CHECKS = [
    "health_check.Database",
    "health_check.Cache",
    "health_check.contrib.psutil.Disk",
    "health_check.contrib.psutil.Memory",
    "health_check.contrib.psutil.CPU",
]
