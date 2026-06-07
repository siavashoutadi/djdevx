from ._base import BasePackage


class DrfFlexFieldsPackage(BasePackage):
    name = "drf-flex-fields"
    packages = ["drf-flex-fields<2"]
    required_dependencies = ["djangorestframework"]


_pkg = DrfFlexFieldsPackage(__file__)
app = _pkg.app
