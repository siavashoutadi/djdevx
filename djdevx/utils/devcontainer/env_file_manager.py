"""Environment file manager for .devcontainer/.env directory."""

import fileinput
from pathlib import Path


class EnvFileManager:
    """
    Manages environment files under the .devcontainer/.env directory.
    Handles adding, removing, and updating environment variable files.
    """

    def __init__(self, project_root: Path):
        self._project_root = project_root

    @property
    def devcontainer_path(self) -> Path:
        return self._project_root / ".devcontainer"

    @property
    def env_path(self) -> Path:
        return self.devcontainer_path / ".env"

    @property
    def env_devcontainer_path(self) -> Path:
        return self.env_path / "devcontainer"

    def add_env_variable(
        self, key: str, value: str, file_path: Path | None = None
    ) -> None:
        """Write KEY=value to the env file, replacing any existing entry for KEY."""
        target = file_path or self.env_devcontainer_path
        self.remove_env_variable(key, target)
        with open(target, "a") as f:
            f.write(f"{key}={value}\n")

    def remove_env_variable(self, key: str, file_path: Path | None = None) -> None:
        """Remove any line starting with KEY= from the env file."""
        target = file_path or self.env_devcontainer_path
        if not target.exists():
            return
        with fileinput.input(target, inplace=True) as f:
            for line in f:
                if not line.startswith(f"{key}="):
                    print(line, end="")

    def add_env_file(self, filename: str, content: str) -> None:
        """Create a new .env file under .env directory.

        Args:
            filename: Name of the file to create (e.g., 'postgres', 'redis').
            content: Content to write to the file.
        """
        env_file = self.env_path / filename
        env_file.parent.mkdir(parents=True, exist_ok=True)
        with open(env_file, "w") as f:
            f.write(content)

    def remove_env_file(self, filename: str) -> None:
        """Remove a .env file from the .env directory.

        Args:
            filename: Name of the file to remove.
        """
        env_file = self.env_path / filename
        if env_file.exists():
            env_file.unlink()
