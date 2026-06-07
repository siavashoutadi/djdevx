from ._base import BasePackage


class DrfNestedRoutersPackage(BasePackage):
    name = "drf-nested-routers"
    packages = ["drf-nested-routers<1"]
    required_dependencies = ["djangorestframework"]


_pkg = DrfNestedRoutersPackage(__file__)
app = _pkg.app
