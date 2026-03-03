import typer
from typing_extensions import Annotated

from .._base import BasePackage


class AzureStoragePackage(BasePackage):
    name = "django-storages Azure"
    packages = ["django-storages[azure]"]

    def install(
        self,
        account_key: Annotated[
            str,
            typer.Option(
                help="The Azure account key for authentication",
                prompt="Please enter the Azure account key for authentication",
            ),
        ] = "",
        account_name: Annotated[
            str,
            typer.Option(
                help="The Azure account name for authentication",
                prompt="Please enter the Azure account name for authentication",
            ),
        ] = "",
        container_name: Annotated[
            str,
            typer.Option(
                help="The Azure container name to store the files in",
                prompt="Please enter the Azure container name to store the files in",
            ),
        ] = "",
    ) -> None:
        """Install django-storages with Azure backend."""
        self._uv_add_all()
        self._copy_templates()

        # Set environment variables
        self.pm.add_env_variable(key="STORAGES_AZURE_ACCOUNT_KEY", value=account_key)
        self.pm.add_env_variable(key="STORAGES_AZURE_ACCOUNT_NAME", value=account_name)
        self.pm.add_env_variable(
            key="STORAGES_AZURE_CONTAINER_NAME", value=container_name
        )

    def remove(self) -> None:
        """Remove django-storages Azure backend and its env vars."""
        super().remove()
        self.pm.remove_env_variable(key="STORAGES_AZURE_ACCOUNT_KEY")
        self.pm.remove_env_variable(key="STORAGES_AZURE_ACCOUNT_NAME")
        self.pm.remove_env_variable(key="STORAGES_AZURE_CONTAINER_NAME")

    def env(
        self,
        account_key: Annotated[
            str,
            typer.Option(
                help="The Azure account key for authentication",
                prompt="Please enter the Azure account key for authentication",
            ),
        ] = "",
        account_name: Annotated[
            str,
            typer.Option(
                help="The Azure account name for authentication",
                prompt="Please enter the Azure account name for authentication",
            ),
        ] = "",
        container_name: Annotated[
            str,
            typer.Option(
                help="The Azure container name to store the files in",
                prompt="Please enter the Azure container name to store the files in",
            ),
        ] = "",
    ) -> None:
        """Configure environment variables for django-storages Azure backend."""
        self.pm.add_env_variable(key="STORAGES_AZURE_ACCOUNT_KEY", value=account_key)
        self.pm.add_env_variable(key="STORAGES_AZURE_ACCOUNT_NAME", value=account_name)
        self.pm.add_env_variable(
            key="STORAGES_AZURE_CONTAINER_NAME", value=container_name
        )


_pkg = AzureStoragePackage(__file__)
app = _pkg.app
