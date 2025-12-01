from settings.django.storages import STORAGES
from settings.utils.env import get_env


env = get_env()


STORAGES.update(
    {
        "default": {
            "BACKEND": "storages.backends.azure_storage.AzureStorage",
            "OPTIONS": {
                "account_key": env("STORAGES_AZURE_ACCOUNT_KEY", default=""),
                "account_name": env("STORAGES_AZURE_ACCOUNT_NAME", default=""),
                "azure_container": env("STORAGES_AZURE_CONTAINER_NAME", default=""),
            },
        }
    }
)
