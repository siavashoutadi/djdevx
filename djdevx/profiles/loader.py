"""Load profiles and answer files from local paths, URLs, or git repos."""

import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import requests
import tomlkit

from .models import AnswersFile, Profile

_BUILTIN_DIR = Path(__file__).resolve().parent / "builtin"
_GIT_PATTERN = re.compile(r"^(.+)@(.+)$")


def resolve_source(source: str) -> Path:
    """Resolve a profile/answers source string to a local file path.

    Supported formats:

    - Local file path: ``./my-profile.toml`` or ``/absolute/path.toml``
    - HTTP/HTTPS URL: ``https://example.com/profiles/multi-page.toml``
    - Git repo with path: ``https://github.com/user/repo.git@api-project.toml``
      Clones the repo (shallow) to a temp directory and returns the file path.
    """
    git_match = _GIT_PATTERN.match(source)
    if git_match:
        repo_url = git_match.group(1)
        file_path = git_match.group(2)
        return _clone_and_read(repo_url, file_path)

    if source.startswith("http://") or source.startswith("https://"):
        return _fetch_url(source)

    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"Profile file not found: {source}")
    return path


def resolve_builtin(name: str) -> Path:
    """Resolve a built-in profile name to its file path.

    Built-in profiles ship with djdevx under ``profiles/builtin/``.
    Raises ``FileNotFoundError`` if the name doesn't match a built-in.
    """
    path = _BUILTIN_DIR / f"{name}.toml"
    if not path.exists():
        available = [f.stem for f in _BUILTIN_DIR.glob("*.toml")]
        raise FileNotFoundError(
            f"Unknown built-in profile '{name}'. "
            f"Available: {', '.join(sorted(available))}"
        )
    return path


def load_profile(source: str | Path) -> Profile:
    """Load and validate a profile from a file path."""
    path = Path(source) if isinstance(source, str) else source
    if not path.exists():
        raise FileNotFoundError(f"Profile file not found: {path}")

    raw = path.read_text()
    data = tomlkit.parse(raw)
    return Profile.model_validate(data)


def load_answers(source: str | Path) -> AnswersFile:
    """Load and validate an answers file from a file path."""
    path = Path(source) if isinstance(source, str) else source
    if not path.exists():
        raise FileNotFoundError(f"Answers file not found: {path}")

    raw = path.read_text()
    data = tomlkit.parse(raw)
    return AnswersFile.model_validate(data)


def list_builtin_profiles() -> list[str]:
    """Return the names of all available built-in profiles."""
    return sorted(f.stem for f in _BUILTIN_DIR.glob("*.toml"))


def autocomplete_profile(incomplete: str) -> list[str]:
    """Built-in profile names matching the incomplete prefix (CLI completion)."""
    return [name for name in list_builtin_profiles() if name.startswith(incomplete)]


def _fetch_url(url: str) -> Path:
    """Download a TOML file from a URL and return a temp file path."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise FileNotFoundError(f"Failed to fetch profile from {url}: {exc}") from exc

    suffix = ".toml"
    parsed = urlparse(url)
    if parsed.path.endswith(".toml"):
        suffix = None

    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=suffix or ".toml", delete=False, prefix="ddx-profile-"
    )
    tmp.write(response.text)
    tmp.close()
    return Path(tmp.name)


def _clone_and_read(repo_url: str, file_path: str) -> Path:
    """Shallow-clone a git repo and return the requested file path."""
    tmp_dir = tempfile.mkdtemp(prefix="ddx-profile-")
    try:
        result = subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, tmp_dir],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise FileNotFoundError(
                f"Failed to clone {repo_url}: {result.stderr.strip()}"
            )

        target = Path(tmp_dir) / file_path
        if not target.exists():
            raise FileNotFoundError(f"File '{file_path}' not found in {repo_url}")
        return target
    except Exception:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise
