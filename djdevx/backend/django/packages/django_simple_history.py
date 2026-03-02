from ._base import BasePackage


class DjangoSimpleHistoryPackage(BasePackage):
    name = "django-simple-history"
    packages = ["django-simple-history"]


_pkg = DjangoSimpleHistoryPackage(__file__)
app = _pkg.app
