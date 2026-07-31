"""Data types for installable config and references."""

from dataclasses import dataclass
from typing import Any, Callable, Optional, cast

from pydantic import BaseModel, ConfigDict, Field

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
    section: str


PACKAGE = InstallableKind("package", "packages")
FEATURE = InstallableKind("feature", "features")
FRAMEWORK = InstallableKind("framework", "frameworks")
DATABASE = InstallableKind("database", "database")
CACHE = InstallableKind("cache", "cache")


@dataclass
class InstallableRef:
    name: str
    kind: InstallableKind


class InstallableConfig(BaseModel):
    """Shared configuration for all installables — single source of truth."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    name: str
    display_name: str = ""
    pixi_packages: list[PixiPackageSpec] = Field(default_factory=list)
    template_path: str = ""
    install_params: list[InstallParam] = Field(default_factory=list)
    needs: list[InstallableRef] = Field(default_factory=list)
    secret_generators: dict[str, Callable] = Field(default_factory=dict)
    files_to_remove: list[str] = Field(default_factory=list)
    folders_to_remove: list[str] = Field(default_factory=list)
    restore_on_remove: dict[str, str] = Field(default_factory=dict)

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
        return value


class Variant(InstallableConfig):
    """A variant of an installable (e.g. "brevo" for anymail, "account" for allauth)."""

    required: bool = False
