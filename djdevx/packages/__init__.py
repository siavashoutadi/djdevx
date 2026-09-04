"""Package CLI — add/remove/list packages with variant selection via questionary."""

from ..cli.factory import domain_app
from ._base import BasePackage
from ._registry import PACKAGE_REGISTRY

app = domain_app(
    BasePackage,
    label="Package",
    registry=PACKAGE_REGISTRY,
    discover_path=__path__,
    discover_name=__name__,
    supports_provider=True,
    supports_multi=True,
)
