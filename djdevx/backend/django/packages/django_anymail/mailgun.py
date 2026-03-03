import typer
from typing_extensions import Annotated

from .._base import BasePackage


class MailgunPackage(BasePackage):
    name = "django-anymail Mailgun"
    packages = ["django-anymail[mailgun]"]

    def install(
        self,
        api_key: Annotated[
            str,
            typer.Option(
                help="The Mailgun API key for authentication",
                prompt="Please enter the Mailgun API key for authentication",
                hide_input=True,
            ),
        ] = "",
        domain: Annotated[
            str,
            typer.Option(
                help="The Mailgun domain",
                prompt="Please enter the Mailgun domain",
            ),
        ] = "",
        default_from_email: Annotated[
            str,
            typer.Option(
                help="The default from email address",
                prompt="Please enter the default from email address",
            ),
        ] = "",
        is_europe: Annotated[
            bool,
            typer.Option(
                help="Flag to use Europe region for Mailgun",
            ),
        ] = False,
    ) -> None:
        """Install django-anymail with Mailgun backend."""
        self._uv_add_all()
        self._copy_templates(context={"is_europe": is_europe})

        self.pm.add_env_variable(key="ANYMAIL_MAILGUN_API_KEY", value=api_key)
        self.pm.add_env_variable(key="ANYMAIL_MAILGUN_SENDER_DOMAIN", value=domain)
        self.pm.add_env_variable(key="DEFAULT_FROM_EMAIL", value=default_from_email)

    def remove(self) -> None:
        """Remove django-anymail Mailgun backend and its env vars."""
        super().remove()
        self.pm.remove_env_variable("ANYMAIL_MAILGUN_API_KEY")
        self.pm.remove_env_variable("ANYMAIL_MAILGUN_SENDER_DOMAIN")
        self.pm.remove_env_variable("DEFAULT_FROM_EMAIL")

    def env(
        self,
        api_key: Annotated[
            str,
            typer.Option(
                help="The Mailgun API key for authentication",
                prompt="Please enter the Mailgun API key for authentication",
                hide_input=True,
            ),
        ] = "",
        domain: Annotated[
            str,
            typer.Option(
                help="The Mailgun domain",
                prompt="Please enter the Mailgun domain",
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
        """Configure environment variables for django-anymail Mailgun backend."""
        self.pm.add_env_variable(key="ANYMAIL_MAILGUN_API_KEY", value=api_key)
        self.pm.add_env_variable(key="ANYMAIL_MAILGUN_SENDER_DOMAIN", value=domain)
        self.pm.add_env_variable(key="DEFAULT_FROM_EMAIL", value=default_from_email)


_pkg = MailgunPackage(__file__)
app = _pkg.app
