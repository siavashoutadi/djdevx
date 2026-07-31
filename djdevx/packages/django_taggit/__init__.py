from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from .._registry import register


@register
class DjangoTaggitPackage(BasePackage):
    name: str = "django-taggit"
    display_name: str = "Django Taggit"
    pixi_packages: list[PixiPackageSpec] = [PixiPackageSpec("django-taggit")]
