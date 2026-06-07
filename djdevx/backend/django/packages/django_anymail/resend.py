from .._base import BasePackage


class ResendPackage(BasePackage):
    name = "django-anymail Resend"
    packages = ["django-anymail[resend]<16"]


_pkg = ResendPackage(__file__)
app = _pkg.app
