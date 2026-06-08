# Creating a Package

This guide walks through adding a new Django package to `djdevx`.

## Step 1: Create the Package Module

Create a new file in `djdevx/backend/django/packages/`:

```python
# djdevx/backend/django/packages/django_example.py
from __future__ import annotations

from djdevx.backend.django.packages._base import BasePackage


class DjangoExamplePackage(BasePackage):
    name = "django-example"
    packages = ["django-example"]
    dev_packages = []
    files_to_remove = []
    folders_to_remove = []


_pkg = DjangoExamplePackage(__file__)
app = _pkg.app
```

If your package depends on another PyPI package that must be installed first,
set `required_dependencies`:

```python
class DjangoExamplePackage(BasePackage):
    name = "django-example"
    packages = ["django-example"]
    required_dependencies = ["some-other-package"]  # checked against pyproject.toml
```

> **Note:** `required_dependencies` checks that a PyPI package name exists in
> `pyproject.toml`. It does not check djdevx sub-package install state — for
> that, override `install()` with a manual check (see `django_allauth/mfa.py`).

## Step 2: Add Install Parameters

For values that need user input during install, use `InstallParam`:

```python
from djdevx.backend.django.packages._base import InstallParam

class DjangoExamplePackage(BasePackage):
    ...
    install_params = [
        InstallParam(
            name="api_version",
            prompt="API version to use",
            default="v2",
        ),
        InstallParam(
            name="enable_webhook",
            prompt="Enable webhook support?",
            default="yes",
        ),
        InstallParam(
            name="webhook_url",
            prompt="Webhook callback URL",
            show_if="enable_webhook",     # only prompted when enable_webhook is True
        ),
    ]
```

The `show_if` parameter references another `InstallParam`'s `name` in the same
list. When that param's value is `True` and this param's value is still empty,
the user is prompted interactively. If the gating param is `False`, this param
is skipped entirely.

Install params become Typer CLI `--options` that are auto-generated at install
time and passed as Jinja2 template context variables.

## Step 3: Create Settings and URL Templates

Config vars and secrets are declared as pydantic `AppBaseSettings` subclasses
in settings templates. Templates live under
`djdevx/templates/django/<template_path>/` (the `template_path` is
auto-derived from your module location — see
[Path Auto-Derivation](package-architecture.md#path-auto-derivation)).

### Settings Template

Create a settings template file:

```
djdevx/templates/django/django_example/
└── settings/
    └── packages/
        └── django_example.py.j2
```

Example settings template:

```python
from backend.settings.utils.base_settings import AppBaseSettings
from pydantic import SecretStr
from typing import Any


class DjangoExampleSettings(AppBaseSettings):
    api_key: SecretStr
    endpoint: str = "https://api.example.com"
    timeout: int = 30

    @classmethod
    def get_dev_defaults(cls) -> dict[str, Any]:
        return {"endpoint": "http://localhost:8000"}

    @classmethod
    def get_prod_defaults(cls) -> dict[str, Any]:
        return {}
```

- `SecretStr` fields are treated as **secrets** (stored in `.secrets/`)
- Non-secret fields (`str`, `int`, `bool`) are treated as **config vars**
- `get_dev_defaults()` provides safe values for local development
- `get_prod_defaults()` should be `{}` -- production must be explicit

### URL Template

If your package needs URL configuration, add a URL template:

```
djdevx/templates/django/django_example/
└── urls/
    └── packages/
        └── django_example.py.j2
```

```python
from django.urls import path, include

urlpatterns = [
    path("api/", include("django_example.urls")),
]
```

### Template Conventions

- Files ending in `.j2` are rendered through Jinja2 and the `.j2` suffix is
  stripped from the output filename (e.g. `django_example.py.j2` →
  `django_example.py`). Non-`.j2` files are copied as-is.
- File and directory names can contain Jinja2 expressions, e.g.
  `{{ package_name }}/__init__.py.j2`.
- The template context includes all `install_params` values plus the project
  name and other scaffolding metadata.

### Auto-Generated Secrets

If a settings template declares `SecretStr` fields that should be
auto-generated during install, register generators on the package class:

```python
from djdevx.utils.generators.password import generate_random_password

class DjangoExamplePackage(BasePackage):
    ...
    secret_generators = {
        "api_key": generate_random_password,
    }
```

Generators are called at the end of `install()` and write their output to
`.secrets/<field_name>`. Skipped if the file already exists (idempotent).

The `SettingCollector` (in `utils/django/setting_collector.py`) discovers both
`SecretStr` and non-secret fields by AST-parsing the generated project's
settings files at runtime. This powers the `ddx backend django settings
configs` and `ddx backend django settings secrets` CLI commands.

### Install Lifecycle

The full install lifecycle is:

```
1. before_uv_install()
2. _check_required_dependencies()
3. _uv_add_all()
4. after_uv_install()
5. before_copy_templates()
6. _copy_templates()
7. after_copy_templates()
8. _write_package_tracking()
9. _generate_secrets()          ← writes .secrets/<field_name>
```

## Step 4: Implement Lifecycle Hooks

Override hooks to customize behavior:

```python
class DjangoExamplePackage(BasePackage):
    ...

    def after_uv_install(self) -> None:
        """Run additional setup after pip install."""
        ...

    def after_copy_templates(self) -> None:
        """Post-template copy actions."""
        ...
```

### Available Hooks

| Hook | Timing |
|------|--------|
| `before_uv_install()` | Before running `uv add` |
| `after_uv_install()` | After running `uv add` |
| `before_copy_templates()` | Before copying template files |
| `after_copy_templates()` | After copying template files |
| `before_uv_remove()` | Before running `uv remove` |
| `after_uv_remove()` | After running `uv remove` |

## Step 5: Registration

Add your package to `djdevx/backend/django/packages/__init__.py`:

```python
from .django_example import app as django_example

app.add_typer(
    django_example,
    name="django-example",
    help="Manage django-example package",
)
```

Each package module exposes a module-level singleton that the `__init__.py`
imports:

```python
_pkg = DjangoExamplePackage(__file__)
app = _pkg.app
```

The `app` is a `typer.Typer()` instance that registers `install` and `remove`
commands for that package.

### Sub-Package Groups

For packages with multiple backends or providers (like `django-storages`,
`django-anymail`, `django-allauth`), create a sub-package directory:

```
django_example_group/
├── __init__.py      # Aggregates sub-packages into one CLI group
├── backend_a.py     # BasePackage subclass
└── backend_b.py     # BasePackage subclass
```

The parent `__init__.py` creates a Typer app and adds each sub-package:

```python
import typer
from .backend_a import app as backend_a_app
from .backend_b import app as backend_b_app

app = typer.Typer(no_args_is_help=True)
app.add_typer(backend_a_app, name="backend-a", help="Backend A")
app.add_typer(backend_b_app, name="backend-b", help="Backend B")
```

Then register the group in the main `packages/__init__.py`:

```python
from .django_example_group import app as example_group

app.add_typer(example_group, name="django-example", help="Manage django-example backends")
```

This produces CLI commands like:

```
ddx backend django packages django-example backend-a install
ddx backend django packages django-example backend-b remove
```

## Step 6: Testing

Create tests in `tests/backend/django/packages/test_<name>.py`:

### Unit Tests

Test package attributes and behavior:

```python
from djdevx.backend.django.packages.django_example import DjangoExamplePackage


class TestDjangoExamplePackage:
    def test_package_attributes(self):
        pkg = DjangoExamplePackage(__file__)
        assert pkg.name == "django-example"
        assert "django-example" in pkg.packages
```

### Integration Tests

Use `CliRunner` and the `create_test_django_backend` fixture for end-to-end
install/remove tests:

```python
import pytest
from typer.testing import CliRunner
from djdevx.backend.django.packages.django_example import app

runner = CliRunner()


class TestDjangoExamplePackageIntegration:
    @pytest.mark.usefixtures("create_test_django_backend")
    def test_install_and_remove(self):
        result = runner.invoke(app, ["install"])
        assert result.exit_code == 0

        result = runner.invoke(app, ["remove"])
        assert result.exit_code == 0
```

### Test Fixtures

Create expected tracking config in
`tests/backend/django/packages/data/django_example/.djdevx/backend/django/packages/django_example/config.toml`:

```toml
[package]
name = "django-example"
```

This fixture verifies that the `write_package_tracking()` step produces the
correct output. See `test_tracking_configs.py` for the test that validates
these fixtures across all packages.

## Full Example

See any existing package for a complete reference:

- **Simple flat package**: `djdevx/backend/django/packages/whitenoise.py`
- **Package with install params**: `djdevx/backend/django/packages/django_meta.py`
- **Package with lifecycle hooks**: `djdevx/backend/django/packages/django_allauth/account.py`
- **Full install() override**: `djdevx/backend/django/packages/django_allauth/mfa.py`
- **Sub-package group**: `djdevx/backend/django/packages/django_storages/__init__.py`
