from .._base import BasePackage


class MailjetPackage(BasePackage):
    name = "django-anymail Mailjet"
    packages = ["django-anymail<16"]


_pkg = MailjetPackage(__file__)
app = _pkg.app
