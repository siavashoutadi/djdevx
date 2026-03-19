from .._base import BasePackage, EnvType, EnvVar


class SESPackage(BasePackage):
    name = "django-anymail SES"
    packages = ["django-anymail[amazon-ses]"]

    env_vars = [
        EnvVar(
            name="access_key",
            env_key="ANYMAIL_SES_ACCESS_KEY",
            help="The AWS access key for authentication",
            prompt="Please enter the AWS access key for authentication",
        ),
        EnvVar(
            name="secret_key",
            env_key="ANYMAIL_SES_SECRET_KEY",
            help="The AWS Secret key for authentication",
            prompt="Please enter the AWS secret key for authentication",
            hide_input=True,
            env_type=EnvType.SECRET,
        ),
        EnvVar(
            name="region_name",
            env_key="ANYMAIL_SES_REGION_NAME",
            help="The AWS region",
            prompt="Please enter the AWS region",
        ),
        EnvVar(
            name="default_from_email",
            env_key="DEFAULT_FROM_EMAIL",
            help="The default from email address",
            prompt="Please enter the default from email address",
        ),
    ]


_pkg = SESPackage(__file__)
app = _pkg.app
