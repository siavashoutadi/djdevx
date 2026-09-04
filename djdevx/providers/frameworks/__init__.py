"""Frameworks CLI — add/remove/list frameworks with auto-discovery."""

from ...cli.factory import domain_app
from ._base import BaseFramework
from ._registry import FRAMEWORK_REGISTRY

app = domain_app(
    BaseFramework,
    label="Framework",
    registry=FRAMEWORK_REGISTRY,
    discover_path=__path__,
    discover_name=__name__,
    supports_multi=True,
)
