from ._base import BasePackage


class DjangoBrowserReloadPackage(BasePackage):
    name = "django-browser-reload"
    dev_packages = ["django-browser-reload<2"]


_pkg = DjangoBrowserReloadPackage(__file__)
app = _pkg.app
