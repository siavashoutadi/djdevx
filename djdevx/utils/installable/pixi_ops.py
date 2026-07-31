"""PixiOps — pixi package operations for installable lifecycle."""

from pathlib import Path
from typing import Optional

from ..project.pixi_runner import PixiRunner
from ..types.pixi_types import PixiPackageSpec
from .types import Variant


class PixiOps:
    def __init__(self, project_root: Path, verbose: bool = False):
        self.pixi = PixiRunner(project_root=project_root, verbose=verbose)

    def add_packages(
        self,
        packages: list[PixiPackageSpec],
        variant: Optional[Variant] = None,
    ) -> None:
        for spec in packages:
            self.pixi.add_from_package_spec(spec, pixi_feature=spec.pixi_feature)
        if variant:
            for spec in variant.pixi_packages:
                self.pixi.add_from_package_spec(spec, pixi_feature=spec.pixi_feature)

    def remove_packages(
        self,
        packages: list[PixiPackageSpec],
        variant: Optional[Variant] = None,
    ) -> None:
        if variant:
            for spec in variant.pixi_packages:
                self.pixi.remove_package_spec_if_exists(
                    spec, pixi_feature=spec.pixi_feature
                )
        else:
            for spec in packages:
                self.pixi.remove_package_spec_if_exists(
                    spec, pixi_feature=spec.pixi_feature
                )
