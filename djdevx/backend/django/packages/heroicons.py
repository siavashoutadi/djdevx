from ._base import BasePackage


class HeroiconsPackage(BasePackage):
    name = "heroicons"
    packages = ["heroicons[django]"]


_pkg = HeroiconsPackage(__file__)
app = _pkg.app
