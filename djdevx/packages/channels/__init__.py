from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from .._registry import register


@register
class ChannelsPackage(BasePackage):
    name: str = "channels"
    display_name: str = "Channels"
    pixi_packages: list[PixiPackageSpec] = [PixiPackageSpec("channels")]
    restore_on_remove: dict[str, str] = {"applications/asgi.py": "applications/asgi.py"}
