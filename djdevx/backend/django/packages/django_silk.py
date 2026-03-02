from ._base import BasePackage


class DjangoSilkPackage(BasePackage):
    name = "django-silk"
    dev_packages = ["django-silk"]


_pkg = DjangoSilkPackage(__file__)
app = _pkg.app
