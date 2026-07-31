from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from .._registry import register


@register
class DjangoRolePermissionsPackage(BasePackage):
    name: str = "django-role-permissions"
    display_name: str = "Django Role Permissions"
    pixi_packages: list[PixiPackageSpec] = [
        PixiPackageSpec("django-role-permissions", kind="pypi")
    ]
