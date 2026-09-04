"""Cache CLI — add/remove/list caches with auto-discovery."""

from ..cli.factory import domain_app
from ._base import BaseCache
from ._registry import CACHE_REGISTRY

app = domain_app(
    BaseCache,
    label="Cache",
    registry=CACHE_REGISTRY,
    discover_path=__path__,
    discover_name=__name__,
    single=True,
)
