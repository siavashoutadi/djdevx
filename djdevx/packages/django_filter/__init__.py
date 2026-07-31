from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from .._registry import register


@register
class DjangoFilterPackage(BasePackage):
    name: str = "django-filter"
    display_name: str = "Django Filter"
    pixi_packages: list[PixiPackageSpec] = [PixiPackageSpec("django-filter")]
