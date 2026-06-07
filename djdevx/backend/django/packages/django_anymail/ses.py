from .._base import BasePackage


class SESPackage(BasePackage):
    name = "django-anymail SES"
    packages = ["django-anymail[amazon-ses]<16"]


_pkg = SESPackage(__file__)
app = _pkg.app
