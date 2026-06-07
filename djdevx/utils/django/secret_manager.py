"""SecretManager — writes and removes per-field secret files under .secrets/."""

import stat
from pathlib import Path


class SecretManager:
    """
    Manages secret files in a .secrets/ or .secrets.prod/ directory.

    pydantic-settings' SecretsSettingsSource reads each AppBaseSettings field
    from a file named after that field inside .secrets/.  This class provides
    a single place to write, remove, and check those files.

    Args:
        project_path: Root of the Django backend (where pyproject.toml lives).
        dir_name: Directory name to use (default: ".secrets").
    """

    def __init__(self, project_path: Path, dir_name: str = ".secrets") -> None:
        self._secrets_dir = project_path / dir_name

    def write_secret(self, key: str, value: str) -> None:
        """Write *value* to .secrets/{key}, creating the directory if needed.

        Args:
            key: Filename inside .secrets/ — must match the pydantic field name
                 on the AppBaseSettings subclass (e.g. ``idp_oidc_private_key``).
            value: The secret value to persist (plain text / PEM / etc.).
        """
        self._secrets_dir.mkdir(exist_ok=True, mode=0o700)
        secret_path = self._secrets_dir / key
        secret_path.write_text(value)
        secret_path.chmod(stat.S_IRUSR | stat.S_IWUSR)

    def remove_secret(self, key: str) -> None:
        """Delete .secrets/{key}.  No-op if the file does not exist.

        Args:
            key: Filename to remove.
        """
        (self._secrets_dir / key).unlink(missing_ok=True)

    def has_secret(self, key: str) -> bool:
        """Return True if .secrets/{key} exists.

        Args:
            key: Filename to check.
        """
        return (self._secrets_dir / key).exists()
