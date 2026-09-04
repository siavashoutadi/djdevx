from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from .._registry import register


@register
class DjangoPermissionsPolicyPackage(BasePackage):
    name: str = "django-permissions-policy"
    display_name: str = "Django Permissions Policy"
    pixi_packages: list[PixiPackageSpec] = [
        PixiPackageSpec("django-permissions-policy", kind="pypi")
    ]
