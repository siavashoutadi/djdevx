from settings import INSTALLED_APPS
from settings.utils.env import get_env


env = get_env()

INSTALLED_APPS.insert(0, "daphne")
INSTALLED_APPS += [
    "channels",
]

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                env("CHANNEL_LAYERS_REDIS_HOST", default="redis://127.0.0.1:6379/1")
            ],
        },
    },
}
