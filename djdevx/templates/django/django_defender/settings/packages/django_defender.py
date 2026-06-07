from typing import Any

from pydantic import AnyUrl

from settings.django.base import INSTALLED_APPS, MIDDLEWARE
from settings.utils.base_settings import AppBaseSettings


class DefenderSettings(AppBaseSettings):
    defender_redis_name: str = "default"
    defender_lockout_url: AnyUrl

    @classmethod
    def get_dev_defaults(cls) -> dict[str, Any]:
        return {"defender_lockout_url": "http://localhost:8000/"}


_defender = DefenderSettings()

INSTALLED_APPS += [
    "defender",
]

MIDDLEWARE += [
    "defender.middleware.FailedLoginMiddleware",
]

DEFENDER_REDIS_NAME = _defender.defender_redis_name
DEFENDER_LOCKOUT_URL = _defender.defender_lockout_url
