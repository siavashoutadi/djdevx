# Deployment Architecture

## Overview

The deployment module (`djdevx/deployment/`) generates production deployment manifests
for container orchestration platforms. It follows the same plugin pattern as the
package system — each target (Docker Compose, Swarm, Kubernetes, etc.) is a
plugin that inherits from `BaseDeployPlugin`.

```
CLI (ddx deployment) ──► plugin.typer_app ──┬── generate(output_dir, **kwargs)
                                             └── verify(output_dir) → bool
```

## BaseDeployPlugin

Every deployment plugin inherits from `BaseDeployPlugin`
(`djdevx/deployment/_base.py`):

```python
from djdevx.deployment._base import BaseDeployPlugin, DeployParam

class MyTargetPlugin(BaseDeployPlugin):
    name = "My Target"
    generate_params = [
        DeployParam(name="domain", type_=str, help="Domain name"),
    ]

    def generate(self, output_dir: Path, **kwargs: Any) -> None:
        ...

    def verify(self, output_dir: Path) -> bool:
        ...
```

### Class Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Human-readable plugin name (used in CLI messages and default output dir) |
| `generate_params` | `list[DeployParam]` | CLI options for the `generate` command — auto-built from each entry |

### Required Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `generate()` | `(output_dir: Path, **kwargs) -> None` | Write manifest files into `output_dir`. Receives CLI values as kwargs. |
| `verify()` | `(output_dir: Path) -> bool` | Check manifests and configs are ready for deployment. Return `True` if OK. |

### Shared Helpers

Base class provides utilities shared across plugins:

| Helper | Description |
|--------|-------------|
| `_write(path, content)` | Write file if content differs; create parent dirs. Prints "wrote" / "kept" |
| `_write_once(path, content)` | Write only if file doesn't exist — never overwrites |
| `_check_files_exist(*paths) -> bool` | Verify all paths exist, print missing |
| `_indent(text, spaces=2)` | Indent a block of text |
| `_to_env_str(value) -> str` | Convert Python value to env-file string (`None`→`""`, `bool`→`"true"/"false"`, `dict/list`→JSON) |
| `_default_output_dir() -> Path` | Returns `<project_root>/deployment/<plugin-name-kebab>/` |
| `_project_root() -> Path` | Returns the djdevx project root directory |

## DeployParam

`DeployParam` declares a CLI parameter for the `generate` command. Each entry
becomes a `--<name>` option (snake_case converted to kebab-case).

```python
DeployParam(
    name="domain",              # CLI option: --domain
    type_=str,                  # CLI argument type (default str)
    help="Domain name",         # Help text for --help
    default=None,               # No default = required (prompted inside generate)
)
```

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | CLI option name (`--<name>`) and key passed to `generate(**kwargs)` |
| `type_` | `type` | Argument type (`str`, `bool`, `int`, etc.) |
| `help` | `str` | Help text shown in `--help` |
| `default` | `Any` | Default value. `None` means required (prompt user inside `generate()`). |

## CLI Auto-Generation

The `typer_app` property on `BaseDeployPlugin` returns a `typer.Typer` instance
with two commands:

- **`generate`** — options auto-built from `generate_params`. The `--output`
  (`-o`) option is always present and falls back to `_default_output_dir()`.
- **`verify`** — takes `--output` and calls `self.verify(output_dir)`.

Plugins expose a module-level `app`:

```python
# djdevx/deployment/my_target.py
plugin = MyTargetPlugin()
app = plugin.typer_app
```

Registered in `deployment/__init__.py`:

```python
from .my_target import app as my_target_app
app.add_typer(my_target_app, name="my-target", help="My Target: ...")
```

This produces:

```
ddx deployment my-target generate --domain example.com
ddx deployment my-target verify
```

### Prompting Inside generate()

Typer-level `prompt` is not used in deploy params. Instead, plugins prompt
interactively inside `generate()` if a required value is `None`. This keeps the
CLI layer simple and allows future frontends (e.g., GUI) to bypass prompt logic:

```python
def generate(self, output_dir: Path, **kwargs: Any) -> None:
    domain = kwargs.get("domain")
    if domain is None:
        domain = input("Domain name: ")
```

## Verification Pattern

The `verify()` method checks that all required files, secrets, and configs are
in place. It should:

1. Check manifest files exist
2. Check secret files exist (or have resolvable values)
3. Check config variables are set
4. Detect drift between generated files and expected content

Each check prints a status line with `print_console.success` / `print_console.error`.
Return `True` only if all checks pass.

## Adding a New Target

Here's a minimal example adding a Helmfile target:

### 1. Create the plugin

```python
# djdevx/deployment/helmfile.py
from __future__ import annotations

from pathlib import Path
from typing import Any

from djdevx.deployment._base import BaseDeployPlugin, DeployParam


class HelmfilePlugin(BaseDeployPlugin):
    name = "Helmfile"

    generate_params = [
        DeployParam(
            name="domain",
            type_=str,
            help="Domain name for the deployment",
            default=None,
        ),
        DeployParam(
            name="chart_name",
            type_=str,
            help="Helm chart name",
            default="my-app",
        ),
    ]

    def generate(self, output_dir: Path, **kwargs: Any) -> None:
        domain = kwargs.get("domain")
        chart_name = kwargs.get("chart_name", "my-app")
        content = f"domain: {domain}\nchart: {chart_name}\n"
        self._write(output_dir / "helmfile.yaml", content)

    def verify(self, output_dir: Path) -> bool:
        return self._check_files_exist(output_dir / "helmfile.yaml")


plugin = HelmfilePlugin()
app = plugin.typer_app
```

### 2. Register in deployment/__init__.py

```python
from .helmfile import app as helmfile_app
app.add_typer(helmfile_app, name="helmfile", help="Helmfile: generate manifests")
```

### 3. Verify it works

```console
$ ddx deployment helmfile generate --domain example.com
$ ddx deployment helmfile verify
```

## Related

- [Docker Compose User Guide](../user-guide/deployment/docker-compose.md) — How to use deployment commands
