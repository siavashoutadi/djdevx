from ._base import BasePackage


class DjangoRolePermissionsPackage(BasePackage):
    name = "django-role-permissions"
    packages = ["django-role-permissions"]


_pkg = DjangoRolePermissionsPackage(__file__)
app = _pkg.app
