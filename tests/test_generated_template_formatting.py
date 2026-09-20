"""Guard tests: templates copied into generated projects must be formatting-stable.

The generated project's prek.toml runs trailing-whitespace, end-of-file-fixer,
djade, pyupgrade, django-upgrade, and ruff on template files during `ddx new` /
`ddx packages add`. The integration tests cannot catch a formatter rewriting a
template (their projects use --no-git-init, so prek never runs hooks), so these
tests render the templates the way the installer does and exercise the real
formatters here instead.

Any change to a template that a formatter would rewrite is a regression: the
format step would fail on a real (git-initialized) install.
"""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from djdevx.utils.templates.manager import TemplateManager

REPO_ROOT = Path(__file__).resolve().parents[1]
DJADE_TARGET = "6.0"
PYUPGRADE_TARGET = "py313-plus"

# Representative context that mirrors a real install choosing every optional
# flag. This exercises the "enabled" branches of {% if %} across providers so a
# formatter regression can't hide behind an unevaluated conditional.
_RENDER_CONTEXT = {
    "project_name": "my-project",
    "project_description": "A generated project",
    "python_version": "3.14",
    "django_version": "6.0",
    "account_url_prefix": "account",
    "email_subject_prefix": "[My Project]",
    "enable_login_by_code": True,
    "enable_webauthn": True,
    "enable_totp": True,
    "enable_trust": True,
    "passkey_login": True,
    "passkey_signup": True,
    "webauthn_allow_insecure": True,
    "totp_issuer": "My Project",
    "totp_period": 30,
    "totp_digits": 6,
    "totp_tolerance": 1,
    "recovery_code_count": 10,
    "recovery_code_digits": 10,
    "trust_cookie_age_days": 30,
    "is_europe": True,
    "site_name": "My Project",
    "site_domain": "example.com",
    "site_protocol": "https",
    "site_type": "website",
    "default_image_url": "https://example.com/i.png",
    "fb_app_id": "facebook-id",
    "fb_pages": "facebook-pages",
    "fb_publisher": "facebook-publisher",
    "twitter_author": "@author",
    "twitter_site": "@site",
    "twitter_type": "summary",
    "use_og_properties": True,
    "use_schemaorg_properties": True,
    "use_title_tag": True,
    "use_twitter_properties": True,
    "configure_facebook": True,
    "configure_twitter": True,
    "author": "Test Author",
    "keywords": "django, test",
    "locale": "en_US",
    "og_type": "website",
    "site_description": "A test project",
    "site_url": "https://example.com",
    "twitter_card_type": "summary",
    "use_middleware": True,
}


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


def _tool(name: str) -> str:
    """Resolve a formatter binary from the venv first, then PATH.

    The guard tests ship with the tools installed into the same venv as the
    package, so resolving next to ``sys.executable`` avoids the CI/developer
    PATH silently skipping the check.
    """
    local = Path(sys.executable).parent / name
    if local.is_file() and local.stat().st_mode & 0o111:
        return str(local)
    resolved = shutil.which(name)
    if resolved is None:
        pytest.skip(f"{name} not available")
    return resolved


@pytest.fixture(scope="module")
def rendered_tree(tmp_path_factory):
    """Render every template root the way the installer does.

    copy_templates renders ``.j2`` files (normalized to a single trailing
    newline) and copies every other file verbatim — mirroring both the
    ``ddx new`` scaffold and each provider package/feature tree.
    """
    root = tmp_path_factory.mktemp("rendered")
    files: list[Path] = []
    for source in _template_roots():
        dest = root / source.relative_to(REPO_ROOT)
        TemplateManager().copy_templates(
            source_dir=source,
            dest_dir=dest,
            template_context=_RENDER_CONTEXT,
            exclude_dirs=["__pycache__"],
        )
        files.extend(sorted(dest.rglob("*")))

    return root, [f for f in files if f.is_file()]


def _by_suffix(files: list[Path], *suffixes: str) -> list[Path]:
    return [f for f in files if f.suffix in suffixes]


def _display(root: Path, rendered: Path) -> Path:
    """Repo-style relative path for a rendered file (messages / target naming)."""
    return rendered.relative_to(root)


def test_djade_clean_html_templates(rendered_tree):
    root, files = rendered_tree
    html_files = _by_suffix(files, ".html")
    assert html_files, "expected at least one generated HTML template"

    djade = _tool("djade")
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


def test_ruff_clean_python_templates(rendered_tree):
    root, files = rendered_tree
    py_files = _by_suffix(files, ".py")
    assert py_files, "expected at least one generated Python template"

    ruff = _tool("ruff")
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


def test_pyupgrade_clean_python_templates(rendered_tree, tmp_path):
    root, files = rendered_tree
    py_files = _by_suffix(files, ".py")
    assert py_files, "expected at least one generated Python template"

    pyupgrade = _tool("pyupgrade")
    pairs: list[tuple[Path, Path]] = []
    for source in py_files:
        target = tmp_path / _display(root, source)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
        pairs.append((source, target))

    result = subprocess.run(
        [
            pyupgrade,
            f"--{PYUPGRADE_TARGET}",
            *(str(t) for _, t in pairs),
        ],
        capture_output=True,
        text=True,
    )

    rewritten = [s for s, t in pairs if t.read_bytes() != s.read_bytes()]
    assert result.returncode == 0, result.stdout
    assert not rewritten, (
        f"pyupgrade --{PYUPGRADE_TARGET} rewrote generated Python templates:\n"
        + "\n".join(str(p) for p in rewritten)
    )


def test_django_upgrade_clean_python_templates(rendered_tree):
    root, files = rendered_tree
    py_files = _by_suffix(files, ".py")
    assert py_files, "expected at least one generated Python template"

    django_upgrade = _tool("django-upgrade")
    result = subprocess.run(
        [
            django_upgrade,
            "--target-version",
            DJADE_TARGET,
            "--check",
            *(str(p) for p in py_files),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "django-upgrade would rewrite generated Python templates:\n" + result.stdout
    )


def test_no_trailing_whitespace(rendered_tree):
    root, files = rendered_tree
    offenders = []
    for path in files:
        try:
            lines = path.read_text().splitlines()
        except UnicodeDecodeError:
            continue
        for index, line in enumerate(lines, start=1):
            if line.rstrip() != line:
                offenders.append(f"{_display(root, path)}:{index}")
    assert not offenders, (
        "templates contain trailing whitespace (trailing-whitespace hook):\n"
        + "\n".join(offenders)
    )


def test_files_end_with_single_newline(rendered_tree):
    root, files = rendered_tree
    offenders = []
    for path in files:
        try:
            data = path.read_bytes()
        except OSError:
            continue
        if b"\x00" in data or not data:
            continue
        if not data.endswith(b"\n") or data.endswith(b"\n\n"):
            offenders.append(_display(root, path))
    assert not offenders, (
        "templates do not end with a single newline (end-of-file-fixer hook):\n"
        + "\n".join(str(p) for p in offenders)
    )
