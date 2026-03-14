from .._base import BasePackage, EnvParam


class BrevoPackage(BasePackage):
    name = "django-anymail Brevo"
    packages = ["django-anymail[brevo]"]

    env_params = [
        EnvParam(
            name="api_key",
            env_key="ANYMAIL_BREVO_API_KEY",
            help="The Brevo API key for authentication",
            prompt="Please enter the Brevo API key for authentication",
            hide_input=True,
        ),
        EnvParam(
            name="default_from_email",
            env_key="DEFAULT_FROM_EMAIL",
            help="The default from email address",
            prompt="Please enter the default from email address",
        ),
    ]


_pkg = BrevoPackage(__file__)
app = _pkg.app
