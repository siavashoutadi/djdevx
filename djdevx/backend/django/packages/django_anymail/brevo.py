from .._base import BasePackage


class BrevoPackage(BasePackage):
    name = "django-anymail Brevo"
    packages = ["django-anymail[brevo]"]


_pkg = BrevoPackage(__file__)
app = _pkg.app
