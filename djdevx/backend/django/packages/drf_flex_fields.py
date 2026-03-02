from ._base import BasePackage


class DrfFlexFieldsPackage(BasePackage):
    name = "drf-flex-fields"
    packages = ["drf-flex-fields"]


_pkg = DrfFlexFieldsPackage(__file__)
app = _pkg.app
