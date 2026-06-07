from ._base import BasePackage


class DjangoCspPackage(BasePackage):
    name = "django-csp"
    packages = ["django-csp<5"]


_pkg = DjangoCspPackage(__file__)
app = _pkg.app
