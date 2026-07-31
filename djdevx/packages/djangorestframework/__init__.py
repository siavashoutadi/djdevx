from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from .._registry import register


@register
class DjangoRestFrameworkPackage(BasePackage):
    name: str = "djangorestframework"
    display_name: str = "Django REST Framework"
    pixi_packages: list[PixiPackageSpec] = [PixiPackageSpec("djangorestframework")]
