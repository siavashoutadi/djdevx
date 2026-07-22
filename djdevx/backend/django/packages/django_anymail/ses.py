from .._base import BasePackage


class SESPackage(BasePackage):
    name = "django-anymail SES"
    packages = ["django-anymail<16", "boto3>=1.24.6"]


_pkg = SESPackage(__file__)
app = _pkg.app
