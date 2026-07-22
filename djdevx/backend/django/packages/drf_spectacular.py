from ._base import BasePackage


class DrfSpectacularPackage(BasePackage):
    name = "drf-spectacular"
    packages = ["drf-spectacular<1", "drf-spectacular-sidecar<2027"]
    required_dependencies = ["djangorestframework"]


_pkg = DrfSpectacularPackage(__file__)
app = _pkg.app
