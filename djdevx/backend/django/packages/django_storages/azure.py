from .._base import BasePackage, EnvType, EnvVar


class AzureStoragePackage(BasePackage):
    name = "django-storages Azure"
    packages = ["django-storages[azure]"]

    env_vars = [
        EnvVar(
            name="account_key",
            env_key="STORAGES_AZURE_ACCOUNT_KEY",
            help="The Azure account key for authentication",
            prompt="Please enter the Azure account key for authentication",
            env_type=EnvType.SECRET,
        ),
        EnvVar(
            name="account_name",
            env_key="STORAGES_AZURE_ACCOUNT_NAME",
            help="The Azure account name for authentication",
            prompt="Please enter the Azure account name for authentication",
        ),
        EnvVar(
            name="container_name",
            env_key="STORAGES_AZURE_CONTAINER_NAME",
            help="The Azure container name to store the files in",
            prompt="Please enter the Azure container name to store the files in",
        ),
    ]


_pkg = AzureStoragePackage(__file__)
app = _pkg.app
