from pydantic import SecretStr

from settings.utils.base_settings import AppBaseSettings, IS_DEV

if not IS_DEV:

    class S3Settings(AppBaseSettings):
        storages_s3_access_key: SecretStr
        storages_s3_secret_key: SecretStr
        storages_s3_region_name: str
        storages_s3_bucket_name: str

    _s3 = S3Settings()

    STORAGES.update(  # noqa: F821
        {
            "default": {
                "BACKEND": "storages.backends.s3.S3Storage",
                "OPTIONS": {
                    "access_key": _s3.storages_s3_access_key.get_secret_value(),
                    "secret_key": _s3.storages_s3_secret_key.get_secret_value(),
                    "region_name": _s3.storages_s3_region_name,
                    "bucket_name": _s3.storages_s3_bucket_name,
                },
            },
            "staticfiles": {
                "BACKEND": "storages.backends.s3.S3Storage",
            },
        }
    )
