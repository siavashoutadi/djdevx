from ._base import BasePackage


class DjangoFilterPackage(BasePackage):
    name = "django-filter"
    packages = ["django-filter<26"]


_pkg = DjangoFilterPackage(__file__)
app = _pkg.app
