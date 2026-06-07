from ._base import BasePackage


class DjangoPermissionsPolicyPackage(BasePackage):
    name = "django-permissions-policy"
    packages = ["django-permissions-policy<5"]


_pkg = DjangoPermissionsPolicyPackage(__file__)
app = _pkg.app
