from .._base import BasePackage
from djdevx.installable.models import CACHE, InstallableRef
from djdevx.utils.types.pixi_types import PixiPackageSpec
from .._registry import register


@register
class ChannelsPackage(BasePackage):
    name: str = "channels"
    display_name: str = "Channels"
    pixi_packages: list[PixiPackageSpec] = [
        PixiPackageSpec("channels"),
        PixiPackageSpec("channels-redis<5", kind="pypi"),
        PixiPackageSpec("daphne<5", pixi_feature="dev"),
        PixiPackageSpec("types-channels", kind="pypi", pixi_feature="dev"),
    ]
    needs: list[InstallableRef] = [InstallableRef(name="redis", kind=CACHE)]
    restore_on_remove: dict[str, str] = {"applications/asgi.py": "applications/asgi.py"}
