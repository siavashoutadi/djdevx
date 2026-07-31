from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from .._registry import register


@register
class DjangoChannelsRestFrameworkPackage(BasePackage):
    name: str = "djangochannelsrestframework"
    display_name: str = "Django Channels REST Framework"
    pixi_packages: list[PixiPackageSpec] = [
        PixiPackageSpec("djangochannelsrestframework", kind="pypi")
    ]
