from ._base import BasePackage


class DjangoAllowCIDRPackage(BasePackage):
    name = "django-allow-cidr"
    packages = ["django-allow-cidr"]


_pkg = DjangoAllowCIDRPackage(__file__)
app = _pkg.app
