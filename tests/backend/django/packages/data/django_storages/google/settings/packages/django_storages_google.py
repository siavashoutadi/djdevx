from settings.django.base import DEBUG
from settings.django.storages import STORAGES
from settings.utils.env import get_env

from google.oauth2 import service_account


env = get_env()


if not DEBUG:
    GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
        env("STORAGES_GOOGLE_CREDENTIALS", default="")
    )

    STORAGES.update(
        {
            "default": {
                "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
                "OPTIONS": {
                    "bucket_name": env("STORAGES_GOOGLE_BUCKET_NAME", ""),
                    "credentials": GS_CREDENTIALS,
                },
            }
        }
    )
