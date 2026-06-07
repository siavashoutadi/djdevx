from .._base import BasePackage


class BrevoPackage(BasePackage):
    name = "django-anymail Brevo"
    packages = ["django-anymail[brevo]<16"]


_pkg = BrevoPackage(__file__)
app = _pkg.app
