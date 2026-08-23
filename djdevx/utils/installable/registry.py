from typing import Generic, Type, TypeVar

from .types import InstallableConfig, InstallableKind

T = TypeVar("T", bound=InstallableConfig)

REGISTRIES: dict[str, "Registry"] = {}


class Registry(Generic[T]):
    def __init__(self, kind: InstallableKind) -> None:
        self._entries: dict[str, Type[T]] = {}
        self._kind = kind
        self._label = kind.name
        REGISTRIES[kind.name] = self

    @property
    def kind(self) -> InstallableKind:
        return self._kind

    def register(self, cls: Type[T]) -> Type[T]:
        name = cls.get_installable_name()
        self._entries[name] = cls
        return cls

    def get(self, name: str) -> Type[T]:
        name = InstallableConfig.normalize_name(name)
        if name not in self._entries:
            raise KeyError(
                f"Unknown {self._label} '{name}'. "
                f"Available: {', '.join(sorted(self._entries.keys()))}"
            )
        return self._entries[name]

    def names(self) -> list[str]:
        return sorted(self._entries.keys())

    def values(self) -> list[Type[T]]:
        return list(self._entries.values())
