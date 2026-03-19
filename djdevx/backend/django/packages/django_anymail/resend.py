from .._base import BasePackage, EnvType, EnvVar


class ResendPackage(BasePackage):
    name = "django-anymail Resend"
    packages = ["django-anymail[resend]"]

    env_vars = [
        EnvVar(
            name="api_key",
            env_key="ANYMAIL_RESEND_API_KEY",
            help="The Resend API key for authentication",
            prompt="Please enter the Resend API key for authentication",
            hide_input=True,
            env_type=EnvType.SECRET,
        ),
        EnvVar(
            name="default_from_email",
            env_key="DEFAULT_FROM_EMAIL",
            help="The default from email address",
            prompt="Please enter the default from email address",
        ),
    ]


_pkg = ResendPackage(__file__)
app = _pkg.app
