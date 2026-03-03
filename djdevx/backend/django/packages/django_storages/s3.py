import typer
from typing_extensions import Annotated

from .._base import BasePackage


class S3Package(BasePackage):
    name = "django-storages S3"
    packages = ["django-storages[s3]"]

    def install(
        self,
        access_key: Annotated[
            str,
            typer.Option(
                help="The AWS access key for authentication",
                prompt="Please enter the AWS access key for authentication",
            ),
        ] = "",
        secret_key: Annotated[
            str,
            typer.Option(
                help="The AWS Secret key for authentication",
                prompt="Please enter the AWS secret key for authentication",
                hide_input=True,
            ),
        ] = "",
        region_name: Annotated[
            str,
            typer.Option(
                help="The AWS region",
                prompt="Please enter the AWS region",
            ),
        ] = "",
        bucket_name: Annotated[
            str,
            typer.Option(
                help="The AWS bucket name to store the files in",
                prompt="Please enter the AWS bucket name to store the files in",
            ),
        ] = "",
    ) -> None:
        """Install django-storages with S3 backend."""
        self._uv_add_all()
        self._copy_templates()

        # Set environment variables
        self.pm.add_env_variable(key="STORAGES_S3_ACCESS_KEY", value=access_key)
        self.pm.add_env_variable(key="STORAGES_S3_SECRET_KEY", value=secret_key)
        self.pm.add_env_variable(key="STORAGES_S3_REGION_NAME", value=region_name)
        self.pm.add_env_variable(key="STORAGES_S3_BUCKET_NAME", value=bucket_name)

    def remove(self) -> None:
        """Remove django-storages S3 backend and its env vars."""
        super().remove()
        self.pm.remove_env_variable(key="STORAGES_S3_ACCESS_KEY")
        self.pm.remove_env_variable(key="STORAGES_S3_SECRET_KEY")
        self.pm.remove_env_variable(key="STORAGES_S3_REGION_NAME")
        self.pm.remove_env_variable(key="STORAGES_S3_BUCKET_NAME")

    def env(
        self,
        access_key: Annotated[
            str,
            typer.Option(
                help="The AWS access key for authentication",
                prompt="Please enter the AWS access key for authentication",
            ),
        ] = "",
        secret_key: Annotated[
            str,
            typer.Option(
                help="The AWS Secret key for authentication",
                prompt="Please enter the AWS secret key for authentication",
                hide_input=True,
            ),
        ] = "",
        region_name: Annotated[
            str,
            typer.Option(
                help="The AWS region",
                prompt="Please enter the AWS region",
            ),
        ] = "",
        bucket_name: Annotated[
            str,
            typer.Option(
                help="The AWS bucket name to store the files in",
                prompt="Please enter the AWS bucket name to store the files in",
            ),
        ] = "",
    ) -> None:
        """Configure environment variables for django-storages S3 backend."""
        self.pm.add_env_variable(key="STORAGES_S3_ACCESS_KEY", value=access_key)
        self.pm.add_env_variable(key="STORAGES_S3_SECRET_KEY", value=secret_key)
        self.pm.add_env_variable(key="STORAGES_S3_REGION_NAME", value=region_name)
        self.pm.add_env_variable(key="STORAGES_S3_BUCKET_NAME", value=bucket_name)


_pkg = S3Package(__file__)
app = _pkg.app
