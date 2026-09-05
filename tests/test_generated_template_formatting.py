"""Guard tests: templates copied into generated projects must be formatting-stable.

The generated project's prek.toml runs djade, pyupgrade, and ruff on template
files during `ddx new` / `ddx packages add`. The integration tests cannot catch
a formatter rewriting a template (their projects use --no-git-init, so prek
never runs hooks), so these tests exercise the real formatters here instead.

Any change to a template that a formatter would rewrite is a regression: the
format step would fail on a real (git-initialized) install.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DJADE_TARGET = "6.0"


def _template_roots() -> list[Path]:
    """Roots whose files are copied verbatim into generated projects.

    Covers the `ddx new` scaffold (djdevx/new/templates) and every provider
    package/feature template tree (a directory literally named ``templates``
    under djdevx/providers). Deliberately excludes djdevx/create/templates
    (startapp scaffolding) and djdevx/utils/templates (host library).
    """
    roots = [REPO_ROOT / "djdevx" / "new" / "templates"]
    roots.extend(
        sorted((REPO_ROOT / "djdevx" / "providers").rglob("templates"))
        if (REPO_ROOT / "djdevx" / "providers").is_dir()
        else []
    )
    return roots


def _template_files(suffix: str) -> list[Path]:
    files: list[Path] = []
    for root in _template_roots():
        for path in root.rglob(f"*{suffix}"):
            if path.is_file():
                files.append(path)
    return sorted(files)


def _require(executable: str) -> str:
    resolved = shutil.which(executable)
    if resolved is None:
        pytest.skip(f"{executable} not available on PATH")
    return resolved


def test_djade_clean_html_templates():
    html_files = _template_files(".html")
    assert html_files, "expected at least one generated HTML template"

    djade = _require("djade")
    result = subprocess.run(
        [
            djade,
            "--target-version",
            DJADE_TARGET,
            "--check",
            *(str(p) for p in html_files),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "djade --check would reformat generated HTML templates:\n" + result.stdout
    )


def test_pyupgrade_clean_python_templates(tmp_path):
    py_files = _template_files(".py")
    assert py_files, "expected at least one generated Python template"

    pyupgrade = _require("pyupgrade")
    for source in py_files:
        target = tmp_path / source.relative_to(REPO_ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())

    targets = [tmp_path / p.relative_to(REPO_ROOT) for p in py_files]
    result = subprocess.run(
        [pyupgrade, "--py313-plus", *(str(t) for t in targets)],
        capture_output=True,
        text=True,
    )

    rewritten = []
    for source, target in zip(py_files, targets, strict=True):
        if target.read_bytes() != source.read_bytes():
            rewritten.append(source)
    assert result.returncode == 0, result.stdout
    assert not rewritten, (
        "pyupgrade --py313-plus rewrote generated Python templates:\n"
        + "\n".join(str(p) for p in rewritten)
    )


def test_ruff_clean_python_templates():
    py_files = _template_files(".py")
    assert py_files, "expected at least one generated Python template"

    ruff = _require("ruff")
    str_files = [str(p) for p in py_files]

    check = subprocess.run([ruff, "check", *str_files], capture_output=True, text=True)
    assert check.returncode == 0, (
        "ruff check reported findings on generated Python templates:\n" + check.stdout
    )

    fmt = subprocess.run(
        [ruff, "format", "--check", *str_files], capture_output=True, text=True
    )
    assert fmt.returncode == 0, (
        "ruff format --check would reformat generated Python templates:\n" + fmt.stdout
    )
