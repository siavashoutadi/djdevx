"""PixiPackageSpec — a dependency specification for pixi (conda/pypi) packages."""

from typing import Literal, Optional


class PixiPackageSpec:
    """A pixi package dependency with its source kind and optional feature."""

    name: str
    kind: Literal["conda", "pypi"] = "conda"
    pixi_feature: Optional[str] = None

    def __init__(
        self,
        name: str,
        kind: Literal["conda", "pypi"] = "conda",
        pixi_feature: Optional[str] = None,
    ) -> None:
        self.name = name
        self.kind = kind
        self.pixi_feature = pixi_feature

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PixiPackageSpec):
            return NotImplemented
        return (
            self.name == other.name
            and self.kind == other.kind
            and self.pixi_feature == other.pixi_feature
        )

    def __hash__(self) -> int:
        return hash((self.name, self.kind, self.pixi_feature))
