from ._base import BasePackage


class DjangoSilkPackage(BasePackage):
    name = "django-silk"
    dev_packages = ["django-silk<6"]


_pkg = DjangoSilkPackage(__file__)
app = _pkg.app
