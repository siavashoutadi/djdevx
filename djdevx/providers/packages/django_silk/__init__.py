from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from .._registry import register


@register
class DjangoSilkPackage(BasePackage):
    name: str = "django-silk"
    display_name: str = "Django Silk"
    pixi_packages: list[PixiPackageSpec] = [
        PixiPackageSpec("django-silk", pixi_feature="dev")
    ]
