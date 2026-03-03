from ._base import BasePackage


class DjangoChannelsRestFrameworkPackage(BasePackage):
    name = "djangochannelsrestframework"
    packages = ["djangochannelsrestframework"]
    required_dependencies = ["channels"]


_pkg = DjangoChannelsRestFrameworkPackage(__file__)
app = _pkg.app
