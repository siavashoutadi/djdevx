from ._base import BasePackage


class DjangoRestFrameworkPackage(BasePackage):
    name = "Django REST Framework"
    packages = ["djangorestframework"]


_pkg = DjangoRestFrameworkPackage(__file__)
app = _pkg.app
