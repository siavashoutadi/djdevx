from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from .._registry import register


@register
class DjangoExtensionsPackage(BasePackage):
    name: str = "django-extensions"
    display_name: str = "Django Extensions"
    pixi_packages: list[PixiPackageSpec] = [
        PixiPackageSpec("django-extensions", pixi_feature="dev")
    ]
