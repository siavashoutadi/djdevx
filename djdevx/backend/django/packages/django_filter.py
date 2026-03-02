from ._base import BasePackage


class DjangoFilterPackage(BasePackage):
    name = "django-filter"
    packages = ["django-filter"]


_pkg = DjangoFilterPackage(__file__)
app = _pkg.app
