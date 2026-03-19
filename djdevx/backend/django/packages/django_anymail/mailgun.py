from .._base import BasePackage, EnvType, EnvVar, InstallParam


class MailgunPackage(BasePackage):
    name = "django-anymail Mailgun"
    packages = ["django-anymail[mailgun]"]

    install_params = [
        InstallParam(
            name="is_europe",
            type_=bool,
            default=False,
            help="Flag to use Europe region for Mailgun",
        ),
    ]

    env_vars = [
        EnvVar(
            name="api_key",
            env_key="ANYMAIL_MAILGUN_API_KEY",
            help="The Mailgun API key for authentication",
            prompt="Please enter the Mailgun API key for authentication",
            hide_input=True,
            env_type=EnvType.SECRET,
        ),
        EnvVar(
            name="domain",
            env_key="ANYMAIL_MAILGUN_SENDER_DOMAIN",
            help="The Mailgun domain",
            prompt="Please enter the Mailgun domain",
        ),
        EnvVar(
            name="default_from_email",
            env_key="DEFAULT_FROM_EMAIL",
            help="The default from email address",
            prompt="Please enter the default from email address",
        ),
    ]


_pkg = MailgunPackage(__file__)
app = _pkg.app
