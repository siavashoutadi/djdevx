from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from ....utils.installable.types import InstallParam
from .._registry import register


@register
class DjangoWafflePackage(BasePackage):
    name: str = "django-waffle"
    display_name: str = "Django Waffle"
    pixi_packages: list[PixiPackageSpec] = [PixiPackageSpec("django-waffle<6")]

    install_params: list[InstallParam] = [
        InstallParam(
            name="use_middleware",
            type_=bool,
            default=True,
            help="Enable WaffleMiddleware to activate flags/switches per-request",
            prompt="Enable WaffleMiddleware (activates flags/switches per-request)?",
        ),
    ]
