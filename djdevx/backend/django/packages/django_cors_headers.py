from ._base import BasePackage


class DjangoCorsHeadersPackage(BasePackage):
    name = "django-cors-headers"
    packages = ["django-cors-headers<5"]


_pkg = DjangoCorsHeadersPackage(__file__)
app = _pkg.app
