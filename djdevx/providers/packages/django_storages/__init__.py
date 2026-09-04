"""StoragesPackage — django-storages with 3 storage backends."""

from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from ....utils.installable.types import Variant
from .._registry import register


@register
class StoragesPackage(BasePackage):
    name: str = "django-storages"
    display_name: str = "Django Storages"
    pixi_packages: list[PixiPackageSpec] = [
        PixiPackageSpec("django-storages[s3,azure,google]", kind="pypi")
    ]
    exclusive_variants: bool = True
    variants: dict[str, Variant] = {
        "s3": Variant(
            name="s3",
            display_name="Amazon S3",
            template_path="s3",
        ),
        "azure": Variant(
            name="azure",
            display_name="Azure Blob Storage",
            template_path="azure",
        ),
        "google": Variant(
            name="google",
            display_name="Google Cloud Storage",
            template_path="google",
        ),
    }
