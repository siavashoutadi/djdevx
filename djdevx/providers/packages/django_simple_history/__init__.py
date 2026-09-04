from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from .._registry import register


@register
class DjangoSimpleHistoryPackage(BasePackage):
    name: str = "django-simple-history"
    display_name: str = "Django Simple History"
    pixi_packages: list[PixiPackageSpec] = [PixiPackageSpec("django-simple-history")]
