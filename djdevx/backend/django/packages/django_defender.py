from ._base import BasePackage


class DjangoDefenderPackage(BasePackage):
    name = "django-defender"
    packages = ["django-defender<1"]


_pkg = DjangoDefenderPackage(__file__)
app = _pkg.app
