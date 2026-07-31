from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from .._registry import register


@register
class DjangoDefenderPackage(BasePackage):
    name: str = "django-defender"
    display_name: str = "Django Defender"
    pixi_packages: list[PixiPackageSpec] = [
        PixiPackageSpec("django-defender", kind="pypi")
    ]
