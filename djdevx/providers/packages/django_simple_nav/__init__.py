from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from .._registry import register


@register
class DjangoSimpleNavPackage(BasePackage):
    name: str = "django-simple-nav"
    display_name: str = "Django Simple Nav"
    pixi_packages: list[PixiPackageSpec] = [
        PixiPackageSpec("django-simple-nav", kind="pypi")
    ]
