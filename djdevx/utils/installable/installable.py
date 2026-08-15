"""Installable — base for all installables (packages, features, frameworks, etc.)."""

import inspect
from functools import cached_property
from pathlib import Path
from typing import Any, Optional

from pydantic import Field

from ..console.print import print_console
from ..project.project_structure import ProjectStructure
from ..tracking import Section
from .pixi_ops import PixiOps
from .scaffold import (
    cleanup_files,
    copy_templates,
    restore_original_templates,
)
from .secrets import SecretsOps
from .tracking import TrackingOps
from .types import InstallableConfig, Variant


class Installable(InstallableConfig):
    """Base class for all installable items (packages, features, frameworks, etc.).

    Subclasses declare config as class-level attributes. Override lifecycle
    hooks to customize behavior.

    Lifecycle — add:

        before_pixi_install()
        PixiOps(project_root).add_packages(packages, variant)
        after_pixi_install()
        before_copy_templates()
        copy_templates(installable, variant)     # see scaffold.py
        after_copy_templates()
        SecretsOps(project_root).generate(installable, variant)
        TrackingOps(section).track_install(installable, variant)
    Lifecycle — remove:

        before_pixi_remove()
        PixiOps(project_root).remove_packages(packages, variant)
        after_pixi_remove()
        cleanup_files(installable, variant)
        SecretsOps(project_root).remove(installable, variant)
        restore_original_templates(installable)
        TrackingOps(section).remove(name)
    """

    description: str = ""
    section: Section = Section.PACKAGES
    exclusive_variants: bool = False
    variants: dict[str, Variant] = Field(default_factory=dict)
    verbose: bool = Field(default=False, exclude=True, repr=False)

    def model_post_init(self, __context: Any) -> None:
        self._structure: Optional[ProjectStructure] = None
        self._install_context: dict[str, Any] = {}

    @classmethod
    def get_registry(cls):
        raise NotImplementedError

    @cached_property
    def template_dir(self) -> Path:
        return Path(inspect.getfile(self.__class__)).parent / "templates"

    @cached_property
    def new_templates_dir(self) -> Path:
        return Path(__file__).resolve().parent.parent.parent / "new" / "templates"

    @property
    def structure(self) -> ProjectStructure:
        if self._structure is None:
            self._structure = ProjectStructure()
        return self._structure

    def reset_state(self) -> None:
        self._structure = None

    # ------------------------------------------------------------------
    # Lifecycle — add / remove
    # ------------------------------------------------------------------

    def add(
        self,
        variant_name: Optional[str] = None,
        *,
        install_kwargs: Optional[dict[str, Any]] = None,
    ) -> None:
        """Install this item: pixi add -> copy templates -> track -> secrets."""
        variant = self.variants.get(variant_name) if variant_name else None

        if not variant_name and self.exclusive_variants and self.variants:
            raise ValueError(
                f"{self.name} has exclusive variants \u2014 must specify one"
            )

        if install_kwargs is None:
            install_kwargs = {}
        self._install_context = install_kwargs

        self.before_pixi_install()
        PixiOps(self.structure.root, self.verbose).add_packages(
            self.pixi_packages, variant
        )
        print_console.ok("Installed dependency")
        self.after_pixi_install()

        self.before_copy_templates()
        copy_templates(self, variant)
        print_console.ok("Finished configuration")
        self.after_copy_templates()

        SecretsOps(self.structure.root).generate(self, variant)

        TrackingOps(self.section).track_install(self, variant)

    def remove(self, variant_name: Optional[str] = None) -> None:
        """Remove this item: pixi remove -> cleanup -> restore -> untrack."""
        variant = self.variants.get(variant_name) if variant_name else None

        pixi_ops = PixiOps(self.structure.root, self.verbose)
        tracking = TrackingOps(self.section)

        self.before_pixi_remove()

        updated: list[str] = []
        if variant is not None:
            pixi_ops.remove_packages(self.pixi_packages, variant=variant)
            existing = tracking.get_variants(self.name)
            updated = [v for v in existing if v != variant_name]

        if variant is None or not updated:
            pixi_ops.remove_packages(self.pixi_packages)

        print_console.ok("Removed dependency")
        self.after_pixi_remove()

        cleanup_files(self, variant)
        SecretsOps(self.structure.root).remove(self, variant)
        print_console.ok("Finished cleanup")

        if updated:
            tracking.add(self.name, self.display_name, variants=updated)
            return

        restore_original_templates(self)
        tracking.remove(self.name)

    # ------------------------------------------------------------------
    # Lifecycle hooks (override in subclasses)
    # ------------------------------------------------------------------

    def before_pixi_install(self) -> None:
        pass

    def after_pixi_install(self) -> None:
        pass

    def before_copy_templates(self) -> None:
        pass

    def after_copy_templates(self) -> None:
        pass

    def before_pixi_remove(self) -> None:
        pass

    def after_pixi_remove(self) -> None:
        pass
