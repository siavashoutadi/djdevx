import typer
from typing_extensions import Annotated

from .._base import BasePackage


class SESPackage(BasePackage):
    name = "django-anymail SES"
    packages = ["django-anymail[amazon-ses]"]

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
        default_from_email: Annotated[
            str,
            typer.Option(
                help="The default from email address",
                prompt="Please enter the default from email address",
            ),
        ] = "",
    ) -> None:
        """Install django-anymail with SES backend."""
        self._uv_add_all()
        self._copy_templates()

        self.pm.add_env_variable(key="ANYMAIL_SES_ACCESS_KEY", value=access_key)
        self.pm.add_env_variable(key="ANYMAIL_SES_SECRET_KEY", value=secret_key)
        self.pm.add_env_variable(key="ANYMAIL_SES_REGION_NAME", value=region_name)
        self.pm.add_env_variable(key="DEFAULT_FROM_EMAIL", value=default_from_email)

    def remove(self) -> None:
        """Remove django-anymail SES backend and its env vars."""
        super().remove()
        self.pm.remove_env_variable("ANYMAIL_SES_ACCESS_KEY")
        self.pm.remove_env_variable("ANYMAIL_SES_SECRET_KEY")
        self.pm.remove_env_variable("ANYMAIL_SES_REGION_NAME")
        self.pm.remove_env_variable("DEFAULT_FROM_EMAIL")

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
        default_from_email: Annotated[
            str,
            typer.Option(
                help="The default from email address",
                prompt="Please enter the default from email address",
            ),
        ] = "",
    ) -> None:
        """Configure environment variables for django-anymail SES backend."""
        self.pm.add_env_variable(key="ANYMAIL_SES_ACCESS_KEY", value=access_key)
        self.pm.add_env_variable(key="ANYMAIL_SES_SECRET_KEY", value=secret_key)
        self.pm.add_env_variable(key="ANYMAIL_SES_REGION_NAME", value=region_name)
        self.pm.add_env_variable(key="DEFAULT_FROM_EMAIL", value=default_from_email)


_pkg = SESPackage(__file__)
app = _pkg.app
