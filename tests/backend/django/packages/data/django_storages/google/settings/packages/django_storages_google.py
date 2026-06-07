from pydantic import SecretStr

from settings.utils.base_settings import AppBaseSettings, IS_DEV

if not IS_DEV:
    from google.oauth2 import service_account

    class GoogleSettings(AppBaseSettings):
        storages_google_credentials: SecretStr
        storages_google_bucket_name: str

    _google = GoogleSettings()

    GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
        _google.storages_google_credentials.get_secret_value()
    )

    STORAGES.update(  # noqa: F821
        {
            "default": {
                "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
                "OPTIONS": {
                    "bucket_name": _google.storages_google_bucket_name,
                    "credentials": GS_CREDENTIALS,
                },
            },
            "staticfiles": {
                "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
            },
        }
    )
