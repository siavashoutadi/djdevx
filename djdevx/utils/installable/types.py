"""Data types for installable config and references."""

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, Any, Callable, Optional, cast

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..tracking.sections import Section

if TYPE_CHECKING:
    from ..tracking import ProjectTracking
from ..types.pixi_types import PixiPackageSpec


@dataclass
class InstallParam:
    """Declares a CLI parameter collected during add and passed to templates."""

    name: str
    type_: type = str
    default: Any = ""
    help: str = ""
    prompt: Optional[str] = None
    show_if: Optional[str] = None
    message_before_prompt: Optional[str] = None
    hide_input: bool = False


@dataclass(frozen=True)
class InstallableKind:
    name: str
    section: Section


PACKAGE = InstallableKind("package", Section.PACKAGES)
FEATURE = InstallableKind("feature", Section.FEATURES)
FRAMEWORK = InstallableKind("framework", Section.FRAMEWORKS)
DATABASE = InstallableKind("database", Section.DATABASE)
CACHE = InstallableKind("cache", Section.CACHE)

KIND_BY_SECTION: dict[Section, InstallableKind] = {
    kind.section: kind for kind in (PACKAGE, FEATURE, FRAMEWORK, DATABASE, CACHE)
}


@dataclass(frozen=True)
class InstallableRef:
    """Reference to a specific installable (dependency or integration peer).

    The name is normalized (``_`` → ``-``) at construction, so refs compare
    equal to registry and tracking keys without extra handling. Used in
    ``needs`` (auto-installed dependencies) and ``listens_to`` (peers whose
    presence triggers integration hooks) — peers must be declared explicitly,
    one ref per installable.
    """

    name: str
    kind: InstallableKind

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", self.name.replace("_", "-"))


ConditionalCheck = Callable[["ConditionContext"], bool]


class ConditionContext:
    """Everything a ``when`` condition may inspect.

    ``project`` is created lazily on first access, so conditions that only
    look at instance state never pay for loading the tracking file. The peer
    engine injects its already-loaded instance to share state.
    """

    def __init__(
        self,
        installable: "InstallableConfig",
        variant: Optional["Variant"] = None,
        project: Optional["ProjectTracking"] = None,
    ) -> None:
        self.installable = installable
        self.variant = variant
        self._project = project

    @property
    def project(self) -> "ProjectTracking":
        if self._project is None:
            from ..tracking import ProjectTracking

            self._project = ProjectTracking()
        return self._project


@dataclass(frozen=True)
class ConditionalPackage:
    """A pixi package that is included only when a condition passes.

    ``when`` receives a single :class:`ConditionContext` with the owning
    installable (and optionally the active variant and the project tracking):

        def when(ctx): return ctx.installable.use_extra

    Realistic example — add a Redis instrumentation client only while the
    open-telemetry feature is installed:

        from djdevx.utils.installable import when_peer
        from djdevx.utils.installable.types import FEATURE, InstallableRef

        @register
        class RedisCache(BaseCache):
            name = "redis"
            conditional_packages: list[ConditionalPackage] = [
                ConditionalPackage(
                    package=PixiPackageSpec(
                        "opentelemetry-instrumentation-redis", kind="pypi"
                    ),
                    when=when_peer(InstallableRef("open-telemetry", FEATURE)),
                )
            ]
    """

    package: PixiPackageSpec
    when: ConditionalCheck


class InstallableConfig(BaseModel):
    """Shared configuration for all installables — single source of truth."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    name: str
    display_name: str = ""
    section: Section = Section.PACKAGES
    pixi_packages: list[PixiPackageSpec] = Field(default_factory=list)
    conditional_packages: list[ConditionalPackage] = Field(default_factory=list)
    template_path: str = ""
    install_params: list[InstallParam] = Field(default_factory=list)
    needs: list[InstallableRef] = Field(default_factory=list)
    listens_to: list[InstallableRef] = Field(default_factory=list)
    secret_generators: dict[str, Callable] = Field(default_factory=dict)
    files_to_remove: list[str] = Field(default_factory=list)
    folders_to_remove: list[str] = Field(default_factory=list)
    restore_on_remove: dict[str, str] = Field(default_factory=dict)
    variants: "dict[str, Variant]" = Field(default_factory=dict)

    @field_validator("name")
    @classmethod
    def _normalize_name(cls, value: str) -> str:
        return value.replace("_", "-")

    @staticmethod
    def normalize_name(name: str) -> str:
        return name.replace("_", "-")

    @classmethod
    def get_installable_name(cls) -> str:
        field = cls.model_fields["name"]
        value = field.default
        if value is None:
            value = (
                cast(Callable[[], Any], field.default_factory)()
                if field.default_factory
                else None
            )
        if value is None:
            raise AttributeError(
                f"{cls.__name__} must set 'name' (e.g. name: str = \"my-package\")"
            )
        return cls.normalize_name(value)

    @cached_property
    def ref(self) -> InstallableRef:
        """This installable's identity as an ``InstallableRef``."""
        return InstallableRef(name=self.name, kind=KIND_BY_SECTION[self.section])

    def on_peer_added(
        self, peer: "InstallableConfig", variant: Optional["Variant"] = None
    ) -> None:
        """Apply the presence of *peer* (idempotent). Override in subclasses."""

    def on_peer_removed(
        self, peer: "InstallableConfig", variant: Optional["Variant"] = None
    ) -> None:
        """Undo the presence of *peer* (idempotent). Override in subclasses."""


class Variant(InstallableConfig):
    """A variant of an installable (e.g. "brevo" for anymail, "account" for allauth)."""

    required: bool = False
