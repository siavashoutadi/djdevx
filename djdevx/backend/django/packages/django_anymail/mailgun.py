from .._base import BasePackage, InstallParam


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


_pkg = MailgunPackage(__file__)
app = _pkg.app
