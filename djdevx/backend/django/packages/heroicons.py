from ._base import BasePackage


class HeroiconsPackage(BasePackage):
    name = "heroicons"
    packages = ["heroicons[django]<3"]


_pkg = HeroiconsPackage(__file__)
app = _pkg.app
