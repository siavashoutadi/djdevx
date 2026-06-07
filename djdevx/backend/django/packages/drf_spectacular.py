from ._base import BasePackage


class DrfSpectacularPackage(BasePackage):
    name = "drf-spectacular"
    packages = ["drf-spectacular[sidecar]<1"]
    required_dependencies = ["djangorestframework"]


_pkg = DrfSpectacularPackage(__file__)
app = _pkg.app
