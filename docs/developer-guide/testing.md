# Testing

`djdevx` uses [pytest](https://docs.pytest.org/) with
[pytest-xdist](https://github.com/pytest-dev/pytest-xdist) for parallel test
execution.

## Running Tests

```bash
# Run all tests (parallel, auto-detected CPU count)
pixi run pytest

# Run with verbose output
pixi run pytest -v

# Stop on first failure
pixi run pytest -x

# Run a specific test file
pixi run pytest tests/packages/test_whitenoise.py

# Run a specific test class
pixi run pytest tests/packages/test_tracking_configs.py::TestFlatPackageTracking

# Run a specific test function
pixi run pytest tests/packages/test_whitenoise.py::test_whitenoise_install_and_remove

# Run tests matching a keyword expression
pixi run pytest -k "database"

# Run tests matching a keyword class/function name
pixi run pytest -k "TestIsSecretStr"
pixi run pytest -k "test_creates_config"

# List all collected tests without running
pixi run pytest --collect-only

# Enter debugger on first failure
pixi run pytest --pdb -x

# Run only unit tests (marker-based filtering)
pixi run pytest -m unit

# Run only integration tests (slower)
pixi run pytest -m integration

# Skip slow tests
pixi run pytest -m "not slow"

# Control parallelism (e.g., disable parallel execution)
pixi run pytest -n 0
pixi run pytest -p no:xdist
```

## Test Configuration

Defined in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
addopts = "-n auto --tb=short --strict-markers --disable-warnings -v"
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

Key settings:
- `-n auto` — runs tests in parallel across all CPU cores (via `pytest-xdist`)
- `--tb=short` — concise traceback output
- `--strict-markers` — raises error on unknown markers (catches typos)
- `--disable-warnings` — suppresses deprecation warnings
- `-v` — verbose output

## Test Markers

Markers are registered in `pyproject.toml` but are not yet actively used in
test files. Tests rely purely on naming conventions for discovery.

| Marker | Description |
|--------|-------------|
| `unit` | Fast, isolated unit tests (no filesystem or external tools) |
| `integration` | Tests that interact with the filesystem or external tools |
| `slow` | Tests that take longer to run |

Use marker expressions to filter:

```bash
# Skip slow tests
pixi run pytest -m "not slow"
```

To add a marker to a test:

```python
import pytest

@pytest.mark.unit
def test_something_fast():
    ...
```

## Prerequisites

Before running tests, install dev dependencies:

```bash
pixi install --feature dev
```

## Test Structure

Tests mirror the source directory structure. Every subdirectory is a proper
Python package (contains `__init__.py`).

```
tests/
├── conftest.py                      # Shared fixtures (temp_dir)
├── test_helpers.py                  # Shared test utility functions
├── test_new.py                      # Full project scaffolding test
│
├── packages/
│   ├── test_basepackage.py          # BasePackage unit tests (path derivation, hooks, etc.)
│   ├── test_channels.py             # ~35 package-specific tests
│   ├── test_whitenoise.py           # Prototypical package test
│   ├── test_django_allauth.py
│   ├── test_tracking_configs.py     # Tracking config golden-file verification
│   ├── test_storages_combined.py    # Multi-package combined install
│   └── ...
├── cache/
│   └── test_redis.py                # Redis cache install/remove
├── create/
│   └── test_app.py                  # App creation command test
├── database/
│   └── test_postgres.py             # PostgreSQL install/remove
├── features/
│   └── test_pwa.py
├── frameworks/
│   ├── test_bootstrap.py
│   ├── test_frankenui.py
│   ├── test_semantic.py
│   └── test_starting_point_ui.py
├── settings/
│   └── test_source.py
├── list/
│   ├── test_caches.py
│   ├── test_databases.py
│   ├── test_features.py
│   └── test_packages.py
│
└── utils/
    ├── test_cache_tracker.py
    ├── test_database_tracker.py
    ├── test_feature_tracker.py
    └── django/
        ├── test_project_manager.py
        ├── test_secret_manager.py
        └── test_setting_collector.py
```

## Data Fixtures (Golden Files)

When tests generate output files, the expected content is stored in `data/`
directories alongside the test file. These are the "golden files" that test
output is compared against.

```
tests/packages/
├── test_whitenoise.py
└── data/
    └── whitenoise/
        ├── .djdevx/packages/whitenoise/config.toml
        └── settings/packages/whitenoise.py
```

Each package has its own `data/<slug>/` directory containing the exact expected
output of a fresh install. The convention is:

```python
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data" / "whitenoise"

def test_something(temp_dir):
    generated = temp_dir / "output.py"
    expected = DATA_DIR / "output.py"
    assert generated.read_text() == expected.read_text()
```

## Key Fixtures

### `temp_dir` (shared)

Provided by `tests/conftest.py`. Wraps pytest's built-in `tmp_path` to give
each test a unique temporary directory as a `pathlib.Path`.

```python
def test_template_rendering(temp_dir):
    output = temp_dir / "output.txt"
    output.write_text("hello")
    assert output.exists()
```

### `tmp_path` (built-in)

pytest's built-in fixture can be used directly when you don't need an alias:

```python
def test_something(tmp_path: Path):
    d = tmp_path / ".djdevx"
    d.mkdir(parents=True)
    ...
```

### `monkeypatch` (built-in)

Used for changing the working directory without affecting other tests:

```python
def test_cli_command(temp_dir, monkeypatch):
    monkeypatch.chdir(temp_dir)
    result = runner.invoke(app, ["list", "packages"])
    ...
```

### Local fixtures (per-test-file)

Many test files define their own fixtures rather than adding to conftest.py.
This keeps shared scope minimal:

```python
# tests/utils/test_feature_tracker.py
import pytest
from djdevx.utils.tracking.feature_tracking import FeatureTracking

@pytest.fixture
def tracker(tmp_path: Path) -> FeatureTracking:
    return FeatureTracking(project_root=tmp_path)
```

### `create_test_django_backend` (shared helper)

Defined in `tests/test_helpers.py`. Bootstraps a full Django project via the
CLI so subsequent commands have a valid project to operate on:

```python
from tests.test_helpers import create_test_django_backend

def test_package_install(temp_dir):
    runner = CliRunner()
    project_dir = create_test_django_backend(temp_dir, runner)
    os.chdir(temp_dir)
    # ... now run install/remove commands
```

## Testing Patterns

Choose the pattern that best matches what you're testing.

### Pattern A: CLI Integration Tests (install/remove lifecycle)

This is the most common pattern (~35 package tests). Test the full install and
remove lifecycle of a package via the CLI.

```python
import os
from pathlib import Path
from typer.testing import CliRunner
from djdevx.main import app
from djdevx.utils.django.project_manager import DjangoProjectManager
from tests.test_helpers import create_test_django_backend

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "whitenoise"


def test_whitenoise_install_and_remove(temp_dir):
    project_dir = create_test_django_backend(temp_dir, runner)
    os.chdir(temp_dir)

    # --- Install ---
    result = runner.invoke(
        app, ["packages", "add", "whitenoise"]
    )
    assert result.exit_code == 0, f"Install failed: {result.output}"

    # Verify settings file was created
    settings_file = project_dir / "settings" / "packages" / "whitenoise.py"
    assert settings_file.exists()
    assert settings_file.read_text() == (
        DATA_DIR / "settings" / "packages" / "whitenoise.py"
    ).read_text()

    # Verify dependency was added
    assert DjangoProjectManager().has_dependency("whitenoise")

    # --- Remove ---
    result = runner.invoke(
        app, ["packages", "remove", "whitenoise"]
    )
    assert result.exit_code == 0, f"Remove failed: {result.output}"
    assert not settings_file.exists()
    assert not DjangoProjectManager().has_dependency("whitenoise")
```

### Pattern B: Idempotency and Removal Tests

Test that running install multiple times is safe (idempotent), and that
removing an installable that was never installed does not error.

```python
def test_feature_install_idempotent(temp_dir):
    project_dir = create_test_django_backend(temp_dir, runner)
    os.chdir(temp_dir)

    # Install feature twice
    for _ in range(2):
        result = runner.invoke(
            app, ["features", "add", "pwa"]
        )
        assert result.exit_code == 0

    # Verify no duplicate content
    base = (project_dir / "templates" / "_base.html").read_text()
    assert base.count('rel="manifest"') == 1


def test_remove_when_not_installed(temp_dir):
    """Removing something that was never installed should not error."""
    create_test_django_backend(temp_dir, runner)
    os.chdir(temp_dir)

    result = runner.invoke(
        app, ["features", "remove", "pwa"]
    )
    assert result.exit_code == 0
```

### Pattern C: Combined Multi-Package Tests

Test that multiple packages can coexist correctly (e.g., whitenoise + S3).

```python
def test_whitenoise_plus_s3(temp_dir):
    project_dir = create_test_django_backend(temp_dir, runner)
    os.chdir(temp_dir)

    # Install first package
    runner.invoke(app, ["packages", "add", "whitenoise"])
    whitenoise_file = project_dir / "settings" / "packages" / "whitenoise.py"
    assert whitenoise_file.exists()

    # Install second package
    runner.invoke(app, ["packages", "add", "django-storages", "s3"])
    s3_file = project_dir / "settings" / "packages" / "django_storages_s3.py"
    assert s3_file.exists()

    # Both files and dependencies present
    assert whitenoise_file.exists()
    assert DjangoProjectManager().has_dependency("whitenoise")
    assert DjangoProjectManager().has_dependency("django-storages")
```

For behavior that depends on execution order (e.g., STORAGES.update()), use
Python's `exec()` to simulate the runtime behavior:

```python
def test_storages_update_order(temp_dir):
    namespace = {}
    exec("STORAGES = {'default': {...}, 'staticfiles': {...}}", namespace)
    exec("STORAGES.update({'staticfiles': {'BACKEND': 'whitenoise...'}})", namespace)
    exec("STORAGES.update({'default': {'BACKEND': 'storages.s3...'}})", namespace)

    assert namespace["STORAGES"]["default"]["BACKEND"] == "storages.backends.s3.S3Storage"
```

### Pattern D: Isolated Tracker Unit Tests

For testing tracker classes (FeatureTracker, DatabaseTracker, etc.) without
touching the real filesystem, create a local subclass that overrides
`djdevx_root`:

```python
from pathlib import Path
import pytest
import tomlkit
from djdevx.utils.tracking.feature_tracking import FeatureTracking


@pytest.fixture
def tracker(tmp_path: Path) -> FeatureTracking:
    return FeatureTracking(project_root=tmp_path)


class TestWriteFeatureConfig:
    def test_creates_config_toml(self, tracker: FeatureTracking) -> None:
        tracker.add("pwa", "PWA")
        assert tracker.is_installed("pwa")

    def test_overwrite_updates_in_place(self, tracker: FeatureTracking) -> None:
        tracker.add("pwa", "Old")
        tracker.add("pwa", "New")
        assert tracker.is_installed("pwa")


class TestIsInstalled:
    def test_false_before_install(self, tracker: FeatureTracking) -> None:
        assert tracker.is_installed("pwa") is False

    def test_true_after_write(self, tracker: FeatureTracking) -> None:
        tracker.add("pwa", "PWA")
        assert tracker.is_installed("pwa") is True

    def test_false_after_remove(self, tracker: FeatureTracking) -> None:
        tracker.add("pwa", "PWA")
        tracker.remove("pwa")
        assert tracker.is_installed("pwa") is False
```

### Pattern E: Mock-Heavy Unit Tests

For testing logic in isolation, mock dependencies with `unittest.mock.patch`.

**Mocking the filesystem root:**

```python
from unittest.mock import patch, MagicMock
from djdevx.packages._base import BasePackage


def test_package_path_derivation():
    with patch.object(BasePackage, "_derive_djdevx_root") as mock_root:
        mock_root.return_value = Path("/home/user/project")
        pkg = BasePackage("/path/to/packages/whitenoise.py")

    assert pkg._settings_file == "whitenoise.py"
    assert pkg._template_path == "whitenoise"
```

**Dynamic subclass creation for custom test scenarios:**

```python
def _make_pkg(file_path: str, **class_attrs) -> BasePackage:
    """Create a BasePackage subclass with given attrs."""
    mock_path = PACKAGES_PATH / file_path
    attrs = {"name": "test-pkg", "packages": [], **class_attrs}

    with patch.object(BasePackage, "_derive_djdevx_root") as mock_root:
        mock_root.return_value = Path("/home/user/project")
        cls = type("TestPkg", (BasePackage,), attrs)
        pkg = object.__new__(cls)
        pkg._install_context = {}
        pkg.__init__(str(mock_path))

    return pkg
```

**Lifecycle hook order verification (lambda call-order tracking):**

```python
def test_install_hook_order():
    pkg = _make_pkg("whitenoise.py")
    call_order = []

    pkg.before_uv_install = lambda: call_order.append("before_uv_install")
    pkg._check_required_dependencies = lambda: call_order.append("_check_required_deps")
    pkg._uv_add_all = lambda: call_order.append("_uv_add_all")
    pkg.after_uv_install = lambda: call_order.append("after_uv_install")
    pkg.before_copy_templates = lambda: call_order.append("before_copy_templates")
    pkg._copy_templates = lambda context=None: call_order.append("_copy_templates")
    pkg.after_copy_templates = lambda: call_order.append("after_copy_templates")
    pkg._write_package_tracking = lambda: call_order.append("_write_package_tracking")

    pkg.install()

    assert call_order == [
        "before_uv_install",
        "_check_required_deps",
        "_uv_add_all",
        "after_uv_install",
        "before_copy_templates",
        "_copy_templates",
        "after_copy_templates",
        "_write_package_tracking",
    ]
```

**Conditional prompt testing (mocking typer.prompt):**

```python
from unittest.mock import patch

class TestShowIfConditionalPrompt:
    def test_prompt_invoked_when_gating_param_true(self):
        pkg = _make_show_if_pkg()
        pkg._check_required_dependencies = lambda: None
        pkg._uv_add_all = lambda: None
        pkg._copy_templates = lambda context=None: None

        with patch(
            "djdevx.packages._base.typer.prompt",
            return_value="prompted-value",
        ) as mock_prompt:
            pkg.install(enable_feature=True, feature_key="")

        mock_prompt.assert_called_once()
        assert pkg._install_context["feature_key"] == "prompted-value"

    def test_prompt_not_invoked_when_gating_param_false(self):
        pkg = _make_show_if_pkg()
        pkg._check_required_dependencies = lambda: None
        pkg._uv_add_all = lambda: None
        pkg._copy_templates = lambda context=None: None

        with patch("djdevx.packages._base.typer.prompt") as mock_prompt:
            pkg.install(enable_feature=False, feature_key="")

        mock_prompt.assert_not_called()
```

**AST parsing tests (no filesystem needed):**

```python
import ast

class TestIsSecretStr:
    def _parse_annotation(self, code: str) -> ast.expr:
        tree = ast.parse(code)
        return tree.body[0].annotation

    def test_secret_str(self) -> None:
        ann = self._parse_annotation("x: SecretStr")
        assert _is_secret_str(ann) is True

    def test_optional_secret_str(self) -> None:
        ann = self._parse_annotation("x: Optional[SecretStr]")
        assert _is_secret_str(ann) is True

    def test_str_is_not_secret(self) -> None:
        ann = self._parse_annotation("x: str")
        assert _is_secret_str(ann) is False
```

### Pattern F: Tracking Config Golden File Verification

Verifies that every package produces exactly the expected tracking
`config.toml`. Uses `importlib` to dynamically load the real package module:

```python
import importlib
from pathlib import Path
from unittest.mock import patch
from djdevx.packages._base import BasePackage

DATA_DIR = Path(__file__).parent / "data"


def _get_pkg(module_path: str) -> BasePackage:
    return importlib.import_module(module_path)._pkg


def _assert_tracking_config(pkg: BasePackage, data_slug: str, tmp_path: Path) -> None:
    djdevx_root = tmp_path / ".djdevx"

    with patch(
        "djdevx.utils.tracking.package_tracking.PackageTracking.djdevx_root",
        new_callable=lambda: property(lambda self: djdevx_root),
    ):
        pkg._write_package_tracking()

    actual = djdevx_root / "packages" / pkg._template_path / "config.toml"
    expected = DATA_DIR / data_slug / ".djdevx" / "packages" / pkg._template_path / "config.toml"

    assert actual.exists()
    assert expected.exists()
    assert actual.read_text() == expected.read_text()


class TestFlatPackageTracking:
    def test_whitenoise(self, tmp_path):
        pkg = _get_pkg("djdevx.packages.whitenoise")
        _assert_tracking_config(pkg, "whitenoise", tmp_path)

    def test_channels(self, tmp_path):
        pkg = _get_pkg("djdevx.packages.channels")
        _assert_tracking_config(pkg, "channels", tmp_path)
```

### Pattern G: Scaffolding Verification

For tests that generate full project structures, compare every generated file
against a complete fixture directory:

```python
from pathlib import Path
import tomllib
import yaml

DATA_DIR = Path(__file__).parent / "data" / "django"


def test_new_project(temp_dir):
    result = runner.invoke(app, [
        "new",
        "--project-name", "my_project",
        "--project-directory", str(temp_dir),
    ])
    assert result.exit_code == 0

    # Compare every file against fixtures
    for fixture_path in DATA_DIR.rglob("*"):
        if fixture_path.is_file():
            relative = fixture_path.relative_to(DATA_DIR)
            generated = temp_dir / relative
            assert generated.exists(), f"Missing: {relative}"
            assert generated.read_text() == fixture_path.read_text(), (
                f"Content mismatch: {relative}"
            )

    # Structured assertions for specific files
    pyproject = tomllib.loads((temp_dir / "pyproject.toml").read_text())
    assert pyproject["project"]["name"] == "my_project"

    prek_config = tomllib.loads((temp_dir / "prek.toml").read_text())
    assert len(prek_config["repos"]) > 0
```

## Writing New Tests

### Test Location

Place test files in `tests/` mirroring the source module path:

| Source module | Test file |
|---|---|
| `djdevx/packages/whitenoise.py` | `tests/packages/test_whitenoise.py` |
| `djdevx/utils/django/setting_collector.py` | `tests/utils/django/test_setting_collector.py` |

All test subdirectories must contain an `__init__.py`.

### Choosing a Pattern

| Scenario | Recommended Pattern |
|---|---|
| Testing a package install/remove via CLI | **A** (CLI Integration) |
| Testing dependency checks or idempotency | **B** (Dependency/Idempotency) |
| Testing multi-package coexistence | **C** (Combined) |
| Testing tracker classes (Feature/Database/Cache) | **D** (Isolated Tracker) |
| Testing pure logic (path derivation, AST, hooks) | **E** (Mock-Heavy Unit) |
| Verifying tracking config.toml output | **F** (Tracking Golden Files) |
| Testing project scaffolding command | **G** (Scaffolding Verification) |

### Adding Data Fixtures for a New Package

1. Run the install command manually once to see the generated files
2. Create the corresponding files under `tests/packages/data/<slug>/`
   echoing the output structure
3. Write a test that compares `runner.invoke(...)` output against these fixtures

### Test Naming Conventions

- Files: `test_<module_name>.py`
- Classes: `Test<Feature>`
- Functions: `test_<what_is_being_tested>`
- Test class methods: `test_<scenario>`

### Fixture Recommendations

- Use `temp_dir` (from conftest.py) for any test that creates files
- Use `monkeypatch.chdir(temp_dir)` in CLI tests that change working directory
- Define file-specific fixtures locally rather than in conftest.py
- Use `tmp_path` directly for simple Path-based tests

### Linting and Prek

Before pushing, run the prek hooks:

```bash
pixi run prek run --all-files
```

The repository uses ruff for linting and formatting. Test files should follow
the same style as the rest of the codebase.
