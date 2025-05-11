from settings import INSTALLED_APPS
from settings.utils.env import get_env

env = get_env()

INSTALLED_APPS += [
    "health_check",
    "health_check.db",
    "health_check.cache",
    "health_check.contrib.psutil",
    "health_check.contrib.migrations",
]

HEALTH_CHECK_URL = env("HEALTH_CHECK_URL", default="hc")
