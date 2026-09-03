"""Binary downloader for services shipped as release artifacts.

Downloaded binaries live under ``.pixi/devdata/bin/`` so they don't pollute the
running pixi environment and are cleaned up by service ``purge``. This module
does not print; callers use ``print_console`` for user-facing messages.
"""

import platform
import shutil
import stat
import urllib.request
import zipfile
from pathlib import Path
from typing import Optional


def _uname_platform() -> str:
    machine = platform.machine().lower()
    if machine in ("x86_64", "amd64"):
        return "amd64"
    if machine in ("aarch64", "arm64"):
        return "arm64"
    return machine or "amd64"


def _os_name() -> str:
    system = platform.system().lower()
    if system == "darwin":
        return "darwin"
    if system == "linux":
        return "linux"
    return system or "linux"


def platform_key() -> str:
    """Return a ``<os>-<arch>`` key used in GitHub release asset names."""
    return f"{_os_name()}-{_uname_platform()}"


def ensure_executable(path: Path) -> None:
    """Chmod a downloaded binary so it can be executed."""
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def download_and_extract(
    url: str,
    dest_dir: Path,
    *,
    archive_type: str = "tar.gz",
    binary_glob: str = "*",
) -> Optional[Path]:
    """Download *url* and extract *binary_glob* into *dest_dir*.

    Returns the extracted binary path, or None if nothing matched.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    archive_path = dest_dir / f"download.{archive_type}"

    with urllib.request.urlopen(url, timeout=120) as resp:  # noqa: S310 - pinned URL
        archive_path.write_bytes(resp.read())

    try:
        if archive_type == "zip":
            with zipfile.ZipFile(archive_path) as zf:
                zf.extractall(dest_dir)
        else:
            shutil.unpack_archive(str(archive_path), str(dest_dir))
    finally:
        archive_path.unlink(missing_ok=True)

    matches = list(dest_dir.glob(binary_glob))
    if not matches:
        return None

    # Prefer a direct executable file over nested directories.
    executable = next(
        (m for m in matches if m.is_file() and not m.name.endswith((".txt", ".md"))),
        matches[0],
    )
    ensure_executable(executable)
    return executable
