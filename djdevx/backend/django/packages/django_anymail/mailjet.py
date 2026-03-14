from .._base import BasePackage, EnvParam


class MailjetPackage(BasePackage):
    name = "django-anymail Mailjet"
    packages = ["django-anymail[mailjet]"]

    env_params = [
        EnvParam(
            name="api_key",
            env_key="ANYMAIL_MAILJET_API_KEY",
            help="The Mailjet API key for authentication",
            prompt="Please enter the Mailjet API key for authentication",
        ),
        EnvParam(
            name="secret_key",
            env_key="ANYMAIL_MAILJET_SECRET_KEY",
            help="The Mailjet Secret key for authentication",
            prompt="Please enter the Mailjet secret key for authentication",
            hide_input=True,
        ),
        EnvParam(
            name="default_from_email",
            env_key="DEFAULT_FROM_EMAIL",
            help="The default from email address",
            prompt="Please enter the default from email address",
        ),
    ]


_pkg = MailjetPackage(__file__)
app = _pkg.app
