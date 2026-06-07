from ._base import BasePackage


class DjangoHealthCheckPackage(BasePackage):
    name = "django-health-check"
    packages = ["django-health-check<5", "psutil<8"]


_pkg = DjangoHealthCheckPackage(__file__)
app = _pkg.app
