from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from .._registry import register


@register
class DjangoAllowCIDRPackage(BasePackage):
    name: str = "django-allow-cidr"
    display_name: str = "Django Allow CIDR"
    pixi_packages: list[PixiPackageSpec] = [
        PixiPackageSpec("django-allow-cidr", kind="pypi")
    ]
