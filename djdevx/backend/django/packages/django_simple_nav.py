from ._base import BasePackage


class DjangoSimpleNavPackage(BasePackage):
    name = "django-simple-nav"
    packages = ["django-simple-nav"]


_pkg = DjangoSimpleNavPackage(__file__)
app = _pkg.app
