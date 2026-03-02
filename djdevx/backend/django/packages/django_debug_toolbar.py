from ._base import BasePackage


class DjangoDebugToolbarPackage(BasePackage):
    name = "django-debug-toolbar"
    dev_packages = ["django-debug-toolbar"]


_pkg = DjangoDebugToolbarPackage(__file__)
app = _pkg.app
