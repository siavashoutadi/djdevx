"""Installable — base for all installables (packages, features, frameworks, etc.)."""

import inspect
from functools import cached_property
from pathlib import Path
from typing import Any, Optional

from pydantic import Field

from ..utils.console.print import NestedStep, print_console
from .ops.format import format_files
from ..utils.project.project_structure import ProjectStructure
from .ops.pixi import PixiOps
from .peers import sync_on_add, sync_on_remove
from ..utils.tracking import ProjectTracking

from .ops.scaffold import (
    cleanup_files,
    copy_templates,
    restore_original_templates,
    template_output_files,
)
from .ops.secrets import SecretsOps
from .ops.tracking import TrackingOps
from .models import InstallableConfig, Variant  # noqa: F401 — needed for Pydantic forward-ref resolution


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
        peers.sync_on_add(installable, variant)  # see peers.py

    Lifecycle — remove:

        before_pixi_remove()
        PixiOps(project_root).remove_packages(packages, variant)
        after_pixi_remove()
        cleanup_files(installable, variant)
        SecretsOps(project_root).remove(installable, variant)
        restore_original_templates(installable)
        TrackingOps(section).remove(name)
        peers.sync_on_remove(installable, variant)
    """

    description: str = ""
    exclusive_variants: bool = False
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
        # <pkg-root>/installable/lifecycle.py -> <pkg-root>/new/templates
        return Path(__file__).resolve().parents[1] / "new" / "templates"

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
        step=None,
    ) -> None:
        """Install this item: pixi add -> copy templates -> track -> secrets."""
        variant = self.variants.get(variant_name) if variant_name else None

        if not variant_name and self.exclusive_variants and self.variants:
            raise ValueError(f"{self.name} has exclusive variants — must specify one")

        if install_kwargs is None:
            install_kwargs = {}
        self._install_context = install_kwargs

        self.before_pixi_install(step=step)
        pixi_ops = PixiOps(self.structure.root, self.verbose)
        pixi_ops.add_packages(self.pixi_packages, variant)
        (step.ok if step else print_console.ok)("Installed dependency")
        self.after_pixi_install(step=step)

        self.before_copy_templates(step=step)
        copy_templates(self, variant)
        (step.ok if step else print_console.ok)("Finished configuration")
        self.after_copy_templates(step=step)

        copied = template_output_files(self, variant)
        format_files(
            [self.structure.root / f for f in copied], self.structure.root, step=step
        )

        SecretsOps(self.structure.root).generate(self, variant, step=step)

        TrackingOps(self.section).track_install(self, variant)

        sync_on_add(self, variant)

    def remove(
        self,
        variant_name: Optional[str] = None,
        step=None,
    ) -> None:
        """Remove this item: pixi remove -> cleanup -> restore -> untrack."""
        variant = self.variants.get(variant_name) if variant_name else None

        pixi_ops = PixiOps(self.structure.root, self.verbose)
        tracking = TrackingOps(self.section)

        # Capture applied peer packages before untracking
        project = ProjectTracking(self.structure.root)
        applied = project.get_applied_peers(
            self.section, type(self).get_installable_name()
        )

        self.before_pixi_remove(step=step)

        updated: list[str] = []
        if variant is not None:
            pixi_ops.remove_packages(self.pixi_packages, variant=variant)
            existing = tracking.get_variants(type(self).get_installable_name())
            updated = [v for v in existing if v != variant_name]

        if variant is None or not updated:
            pixi_ops.remove_packages(self.pixi_packages)

        (step.ok if step else print_console.ok)("Removed dependency")
        self.after_pixi_remove(step=step)

        cleanup_files(self, variant)
        SecretsOps(self.structure.root).remove(self, variant)
        (step.ok if step else print_console.ok)("Finished cleanup")

        if updated:
            tracking.add(
                type(self).get_installable_name(), self.display_name, variants=updated
            )
            fully_removed = False
        else:
            restore_original_templates(self)
            tracking.remove(type(self).get_installable_name())
            fully_removed = True

        sync_on_remove(self, variant, applied=applied, fully_removed=fully_removed)

    # ------------------------------------------------------------------
    # Lifecycle hooks (override in subclasses)
    # ------------------------------------------------------------------

    def before_pixi_install(self, step: NestedStep | None = None) -> None:
        pass

    def after_pixi_install(self, step: NestedStep | None = None) -> None:
        pass

    def before_copy_templates(self, step: NestedStep | None = None) -> None:
        pass

    def after_copy_templates(self, step: NestedStep | None = None) -> None:
        pass

    def before_pixi_remove(self, step: NestedStep | None = None) -> None:
        pass

    def after_pixi_remove(self, step: NestedStep | None = None) -> None:
        pass
