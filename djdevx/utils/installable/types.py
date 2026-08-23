"""Data types for installable config and references."""

from dataclasses import dataclass
from typing import Any, Callable, Optional, cast

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..tracking.sections import Section
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
    """Typed reference to a specific installable (dependency or integration peer).

    The name is normalized (``_`` → ``-``) at construction, so refs compare
    equal to registry and tracking keys without extra handling.
    """

    name: str
    kind: InstallableKind

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", self.name.replace("_", "-"))


ConditionalCheck = Callable[..., bool]


@dataclass(frozen=True)
class ConditionalPackage:
    """A single pixi package guarded by an arbitrary condition.

    ``when`` is called with the owning installable instance as its first
    positional argument. Return True to include the package, False to skip it.
    """

    package: PixiPackageSpec
    when: ConditionalCheck


class InstallableConfig(BaseModel):
    """Shared configuration for all installables — single source of truth."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    name: str
    display_name: str = ""
    pixi_packages: list[PixiPackageSpec] = Field(default_factory=list)
    conditional_packages: list[ConditionalPackage] = Field(default_factory=list)
    template_path: str = ""
    install_params: list[InstallParam] = Field(default_factory=list)
    needs: list[InstallableRef] = Field(default_factory=list)
    secret_generators: dict[str, Callable] = Field(default_factory=dict)
    files_to_remove: list[str] = Field(default_factory=list)
    folders_to_remove: list[str] = Field(default_factory=list)
    restore_on_remove: dict[str, str] = Field(default_factory=dict)

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


class Variant(InstallableConfig):
    """A variant of an installable (e.g. "brevo" for anymail, "account" for allauth)."""

    required: bool = False
