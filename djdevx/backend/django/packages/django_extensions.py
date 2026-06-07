from ._base import BasePackage


class DjangoExtensionsPackage(BasePackage):
    name = "django-extensions"
    packages = ["django-extensions<5"]


_pkg = DjangoExtensionsPackage(__file__)
app = _pkg.app
