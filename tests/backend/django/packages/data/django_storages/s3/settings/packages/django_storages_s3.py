from settings.django.storages import STORAGES
from settings.utils.env import get_env


env = get_env()

STORAGES.update(
    {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                "access_key": env("STORAGES_S3_ACCESS_KEY", default=""),
                "secret_key": env("STORAGES_S3_SECRET_KEY", default=""),
                "region_name": env("STORAGES_S3_REGION_NAME", default=""),
                "bucket_name": env("STORAGES_S3_BUCKET_NAME", default=""),
            },
        }
    }
)
