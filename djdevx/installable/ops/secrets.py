"""SecretsOps — secret generation and removal for installables."""

from pathlib import Path
from typing import Any

from ...utils.console.print import print_console
from ...utils.project.secret_manager import SecretManager


class SecretsOps:
    def __init__(self, project_root: Path):
        self._secret_manager = SecretManager(project_root)

    def generate(self, installable, variant=None, step=None) -> None:
        generators: dict[str, Any] = {}
        generators.update(installable.secret_generators)
        if variant:
            generators.update(variant.secret_generators)
        for field_name, generator in generators.items():
            if not self._secret_manager.has_secret(field_name):
                value = generator()
                self._secret_manager.write_secret(field_name, value)
                if step is not None:
                    step.ok(f"  Generated secret: {field_name}")
                else:
                    print_console.ok(f"  Generated secret: {field_name}")

    def remove(self, installable, variant=None) -> None:
        generators: dict[str, Any] = {}
        generators.update(installable.secret_generators)
        if variant:
            generators.update(variant.secret_generators)
        for field_name in generators:
            self._secret_manager.remove_secret(field_name)
