from settings import BASE_DIR
from settings.utils.env import is_local, get_env

env = get_env()

# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
if is_local():
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
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
