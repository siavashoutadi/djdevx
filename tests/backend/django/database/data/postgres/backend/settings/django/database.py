from settings.utils.env import get_env

env = get_env()

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "PORT": env("POSTGRES_PORT", default="5432"),
        "HOST": env("POSTGRES_SERVER", default="localhost"),
        "NAME": env("POSTGRES_DB", default=""),
        "USER": env("POSTGRES_USER", default=""),
        "PASSWORD": env("POSTGRES_PASSWORD", default=""),
    }
}
