from pydantic import SecretStr

from settings.utils.base_settings import AppBaseSettings, IS_DEV

if not IS_DEV:

    class AzureSettings(AppBaseSettings):
        storages_azure_account_key: SecretStr
        storages_azure_account_name: str
        storages_azure_container_name: str

    _azure = AzureSettings()

    STORAGES.update(  # noqa: F821
        {
            "default": {
                "BACKEND": "storages.backends.azure_storage.AzureStorage",
                "OPTIONS": {
                    "account_key": _azure.storages_azure_account_key.get_secret_value(),
                    "account_name": _azure.storages_azure_account_name,
                    "azure_container": _azure.storages_azure_container_name,
                },
            },
            "staticfiles": {
                "BACKEND": "storages.backends.azure_storage.AzureStorage",
            },
        }
    )
