"""Binary downloader for services shipped as release artifacts.

Downloaded binaries live under ``.pixi/devdata/bin/`` so they don't pollute the
running pixi environment and are cleaned up by service ``purge``. This module
does not print; callers use ``print_console`` for user-facing messages.

Every supported release URL is pinned to an exact version together with the
SHA256 checksum published by the upstream project, and the downloaded bytes are
verified *before* anything is extracted or executed.
"""

import hashlib
import platform
import shutil
import stat
import urllib.request
import zipfile
from pathlib import Path
from typing import Optional

# Pinned release versions (kept in sync with the devcontainer images in
# djdevx/features/otel/__init__.py).
OTELCOL_CONTRIB_VERSION = "0.159.0"
OPENOBSERVE_VERSION = "v0.92.2"

# Upstream-published SHA256 checksums keyed by ``platform_key()``.
_OTELCOL_CONTRIB_SHA256: dict[str, str] = {
    "linux-amd64": "9d589f6349f01179957a2052bc7307a99db2efc971e14e00575941a77122eaaf",
    "linux-arm64": "abb8665cc963e886c2d1286c50b38bcb2e53d968b192c3d8fe4d1ed6b91c3901",
    "darwin-amd64": "c683fc414117b8477794dcd7591e84e61cbef1e2ff8817afb6fd622e7fb5c0d9",
    "darwin-arm64": "7e317b75b1b087ba2150bf95d79e39a394d0d091f1231af6bbebee895d200375",
}
_OPENOBSERVE_SHA256: dict[str, str] = {
    "linux-amd64": "2b9d35034a6810a6a2043447055cfa493f9302c0402f5a83728efc9f848b68a9",
    "linux-arm64": "efa8d4593a99dbf9d94e26d854c2e7a789e03f7b89eff6c8882b973d09268dec",
    "darwin-amd64": "a79e73140000f313d841a00520ff2cdee6e1486dfb2042083106467793124970",
    "darwin-arm64": "4bb8be58945b8930d7f18d0fdb924eab8c71a67582e81f6b5663bf079a8adc66",
    "windows-amd64": "969a74b87e7d9fc902969149140be4ccfd72e24428623a6989e7f1fef5cc10ca",
}


def _pinned(table: dict[str, str], what: str) -> tuple[str, str]:
    """Return ``(platform_key, sha256)`` or fail loudly for unsupported platforms."""
    key = platform_key()
    digest = table.get(key)
    if digest is None:
        raise RuntimeError(
            f"No pinned {what} release for platform '{key}'; refusing to download."
        )
    return key, digest


def otelcol_contrib_release_url() -> str:
    """Pinned GitHub release URL for the otelcol-contrib tarball."""
    key, _ = _pinned(_OTELCOL_CONTRIB_SHA256, "otelcol-contrib")
    v = OTELCOL_CONTRIB_VERSION
    # GitHub asset names use ``<os>_<arch>`` (underscores), not ``<os>-<arch>``.
    asset_key = key.replace("-", "_")
    return (
        "https://github.com/open-telemetry/opentelemetry-collector-releases"
        f"/releases/download/v{v}/otelcol-contrib_{v}_{asset_key}.tar.gz"
    )


def otelcol_contrib_sha256() -> str:
    """Upstream-published SHA256 of the pinned otelcol-contrib tarball."""
    return _pinned(_OTELCOL_CONTRIB_SHA256, "otelcol-contrib")[1]


def openobserve_release_url() -> str:
    """Pinned download URL for the OpenObserve (open source) release archive."""
    key, _ = _pinned(_OPENOBSERVE_SHA256, "openobserve")
    v = OPENOBSERVE_VERSION
    ext = "zip" if key.startswith("windows") else "tar.gz"
    return (
        f"https://downloads.openobserve.ai/releases/openobserve/{v}"
        f"/openobserve-{v}-{key}.{ext}"
    )


def openobserve_sha256() -> str:
    """Upstream-published SHA256 of the pinned OpenObserve archive."""
    return _pinned(_OPENOBSERVE_SHA256, "openobserve")[1]


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
    expected_sha256: Optional[str] = None,
) -> Optional[Path]:
    """Download *url* and extract *binary_glob* into *dest_dir*.

    When *expected_sha256* is given the archive digest is verified before any
    extraction; a mismatch aborts with ``RuntimeError`` and nothing is written
    to disk. Returns the extracted binary path, or None if nothing matched.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    archive_path = dest_dir / f"download.{archive_type}"

    with urllib.request.urlopen(url, timeout=120) as resp:  # noqa: S310 - pinned URL
        payload = resp.read()

    if expected_sha256 is not None:
        digest = hashlib.sha256(payload).hexdigest()
        if digest != expected_sha256.lower():
            archive_path.unlink(missing_ok=True)
            raise RuntimeError(
                f"SHA256 mismatch for {url}: expected {expected_sha256}, "
                f"got {digest}. Refusing to extract the download."
            )
    archive_path.write_bytes(payload)

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
