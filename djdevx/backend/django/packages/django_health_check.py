from ._base import BasePackage


class DjangoHealthCheckPackage(BasePackage):
    name = "django-health-check"
    packages = ["django-health-check>=4.0.0,<5", "psutil"]


_pkg = DjangoHealthCheckPackage(__file__)
app = _pkg.app
