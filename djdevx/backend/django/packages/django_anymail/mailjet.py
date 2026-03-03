import typer
from typing_extensions import Annotated

from .._base import BasePackage


class MailjetPackage(BasePackage):
    name = "django-anymail Mailjet"
    packages = ["django-anymail[mailjet]"]

    def install(
        self,
        api_key: Annotated[
            str,
            typer.Option(
                help="The Mailjet API key for authentication",
                prompt="Please enter the Mailjet API key for authentication",
            ),
        ] = "",
        secret_key: Annotated[
            str,
            typer.Option(
                help="The Mailjet Secret key for authentication",
                prompt="Please enter the Mailjet secret key for authentication",
                hide_input=True,
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
        """Install django-anymail with Mailjet backend."""
        self._uv_add_all()
        self._copy_templates()

        self.pm.add_env_variable(key="ANYMAIL_MAILJET_API_KEY", value=api_key)
        self.pm.add_env_variable(key="ANYMAIL_MAILJET_SECRET_KEY", value=secret_key)
        self.pm.add_env_variable(key="DEFAULT_FROM_EMAIL", value=default_from_email)

    def remove(self) -> None:
        """Remove django-anymail Mailjet backend and its env vars."""
        super().remove()
        self.pm.remove_env_variable("ANYMAIL_MAILJET_API_KEY")
        self.pm.remove_env_variable("ANYMAIL_MAILJET_SECRET_KEY")
        self.pm.remove_env_variable("DEFAULT_FROM_EMAIL")

    def env(
        self,
        api_key: Annotated[
            str,
            typer.Option(
                help="The Mailjet API key for authentication",
                prompt="Please enter the Mailjet API key for authentication",
            ),
        ] = "",
        secret_key: Annotated[
            str,
            typer.Option(
                help="The Mailjet Secret key for authentication",
                prompt="Please enter the Mailjet secret key for authentication",
                hide_input=True,
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
        """Configure environment variables for django-anymail Mailjet backend."""
        self.pm.add_env_variable(key="ANYMAIL_MAILJET_API_KEY", value=api_key)
        self.pm.add_env_variable(key="ANYMAIL_MAILJET_SECRET_KEY", value=secret_key)
        self.pm.add_env_variable(key="DEFAULT_FROM_EMAIL", value=default_from_email)


_pkg = MailjetPackage(__file__)
app = _pkg.app
