from ._base import BasePackage


class DjangoBrowserReloadPackage(BasePackage):
    name = "django-browser-reload"
    dev_packages = ["django-browser-reload"]


_pkg = DjangoBrowserReloadPackage(__file__)
app = _pkg.app
