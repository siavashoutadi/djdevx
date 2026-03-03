from ._base import BasePackage


class DrfFlexFieldsPackage(BasePackage):
    name = "drf-flex-fields"
    packages = ["drf-flex-fields"]
    required_dependencies = ["djangorestframework"]


_pkg = DrfFlexFieldsPackage(__file__)
app = _pkg.app
