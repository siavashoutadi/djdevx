from pathlib import Path

import typer
from typing_extensions import Annotated

from .._base import BasePackage


class GoogleStoragePackage(BasePackage):
    name = "django-storages Google Cloud Storage"
    packages = ["django-storages[google]"]

    def install(
        self,
        credentials_file_path: Annotated[
            Path,
            typer.Option(
                help="The path to the google credential file",
                prompt="Please enter the path to the google credential file",
            ),
        ] = None,
        bucket_name: Annotated[
            str,
            typer.Option(
                help="The Google bucket name to store the files in",
                prompt="Please enter the Google bucket name to store the files in",
            ),
        ] = "",
    ) -> None:
        """Install django-storages with Google Cloud Storage backend."""
        self._uv_add_all()
        self._copy_templates()

        # Set environment variables
        self.pm.add_env_variable(
            key="STORAGES_GOOGLE_CREDENTIALS", value=str(credentials_file_path)
        )
        self.pm.add_env_variable(key="STORAGES_GOOGLE_BUCKET_NAME", value=bucket_name)

    def remove(self) -> None:
        """Remove django-storages Google backend and its env vars."""
        super().remove()
        self.pm.remove_env_variable(key="STORAGES_GOOGLE_CREDENTIALS")
        self.pm.remove_env_variable(key="STORAGES_GOOGLE_BUCKET_NAME")

    def env(
        self,
        credentials_file_path: Annotated[
            Path,
            typer.Option(
                help="The path to the google credential file",
                prompt="Please enter the path to the google credential file",
            ),
        ] = None,
        bucket_name: Annotated[
            str,
            typer.Option(
                help="The Google bucket name to store the files in",
                prompt="Please enter the Google bucket name to store the files in",
            ),
        ] = "",
    ) -> None:
        """Configure environment variables for django-storages Google backend."""
        self.pm.add_env_variable(
            key="STORAGES_GOOGLE_CREDENTIALS", value=str(credentials_file_path)
        )
        self.pm.add_env_variable(key="STORAGES_GOOGLE_BUCKET_NAME", value=bucket_name)


_pkg = GoogleStoragePackage(__file__)
app = _pkg.app
