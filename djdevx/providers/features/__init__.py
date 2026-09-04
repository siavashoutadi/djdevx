"""Features CLI — add/remove/list features with auto-discovery."""

from ...cli.factory import domain_app
from ._base import BaseFeature
from ._registry import FEATURE_REGISTRY

app = domain_app(
    BaseFeature,
    label="Feature",
    registry=FEATURE_REGISTRY,
    discover_path=__path__,
    discover_name=__name__,
    supports_provider=True,
    supports_multi=True,
)
