import typer
from typing_extensions import Annotated

from .._base import BasePackage


class BrevoPackage(BasePackage):
    name = "django-anymail Brevo"
    packages = ["django-anymail[brevo]"]

    def install(
        self,
        api_key: Annotated[
            str,
            typer.Option(
                help="The Brevo API key for authentication",
                prompt="Please enter the Brevo API key for authentication",
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
        """Install django-anymail with Brevo backend."""
        self._uv_add_all()
        self._copy_templates()

        self.pm.add_env_variable(key="ANYMAIL_BREVO_API_KEY", value=api_key)
        self.pm.add_env_variable(key="DEFAULT_FROM_EMAIL", value=default_from_email)

    def remove(self) -> None:
        """Remove django-anymail Brevo backend and its env vars."""
        super().remove()
        self.pm.remove_env_variable("ANYMAIL_BREVO_API_KEY")
        self.pm.remove_env_variable("DEFAULT_FROM_EMAIL")

    def env(
        self,
        api_key: Annotated[
            str,
            typer.Option(
                help="The Brevo API key for authentication",
                prompt="Please enter the Brevo API key for authentication",
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
        """Configure environment variables for django-anymail Brevo backend."""
        self.pm.add_env_variable(key="ANYMAIL_BREVO_API_KEY", value=api_key)
        self.pm.add_env_variable(key="DEFAULT_FROM_EMAIL", value=default_from_email)


_pkg = BrevoPackage(__file__)
app = _pkg.app
