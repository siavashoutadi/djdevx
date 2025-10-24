# AI Agent Instructions for djdevx

This guide provides essential context and step-by-step procedures for AI agents working with the djdevx codebase. djdevx is a Django project scaffolding system built on Typer CLI and Jinja2 templating that streamlines Django development.

## Architecture Overview

### Core Components
- **CLI Structure**: Built with Typer, organized in `djdevx/main.py` with subcommands in packages/, create/, feature/
- **Template System**: Uses Jinja2 for generating project files from templates in `djdevx/templates/`
- **Settings Management**: Modular settings split into django/, packages/, apps/ for easy maintenance
- **URL Routing**: Separate URL configurations for core Django, packages, and apps
- **Package Manager**: Modular system where each Django package has isolated settings/URLs

### Key Directories
```
djdevx/
├── templates/            # Jinja2 templates for project generation
│   ├── init/            # Project initialization templates
│   └── {package-name}/  # Package-specific templates
├── packages/            # Package management commands
├── create/             # Application creation tools
├── feature/            # Feature addition (PWA, CSS frameworks)
└── utils/              # Shared utilities
```

---

## Step-by-Step Procedures

### 1. Adding a New Package Integration

This guide covers adding Django package support to djdevx. Follow these steps systematically.

#### Step 1.1: Research Package Requirements

**CRITICAL**: Before writing any code, research the package thoroughly:

1. **Search the package's official documentation** for:
   - Required settings (INSTALLED_APPS entries, middleware, configuration)
   - Required URL patterns (if any)
   - Environment variables or secrets needed
   - Dependencies on other Django packages
   - Backend variants (like django-storages having S3, Azure, Google backends)

2. **Look for official installation guides** and note:
   - PyPI package name (exact name for `uv add`)
   - Optional extras (e.g., `django-storages[s3]`)
   - Whether it's a dev dependency or production dependency

3. **Identify configuration categories**:
   - Settings that are **secrets** (API keys, passwords) → need `env` command
   - Settings that are **environment-specific** (URLs, paths) → use environment variables with defaults
   - Settings that are **static/secure defaults** → hardcode in settings template
   - Settings that are **user choices** → need Typer arguments + Jinja2 templating

#### Step 1.2: Determine Package Structure (Single vs Multi-Action)

**Single-Action Package** (one installation method):
- Example: `django-browser-reload`, `django-debug-toolbar`
- Create: `djdevx/packages/{package_name}.py`
- Structure: One Typer app with `install()`, `remove()`, and optionally `env()` commands

**Multi-Action Package** (multiple installation variants/backends):
- Example: `django-storages` (S3, Azure, Google), `django-allauth` (providers)
- Create: `djdevx/packages/{package_name}/` directory with:
  - `__init__.py` - Main Typer app that combines sub-apps
  - `install.py` - Multiple install commands (one per variant)
  - `remove.py` - Unified remove command
  - `env.py` - Environment variable setup per variant

**Decision rule**: If the package has multiple backends, providers, or significantly different installation methods, use multi-action structure.

#### Step 1.3: Create Package Command File(s)

**For Single-Action Packages:**

Always look for existing single-action packages for reference such as `django_meta.py`.

Create `djdevx/packages/{package_name}.py`:

```python
import subprocess
import typer
from pathlib import Path

from ..utils.print_console import print_step, print_success, print_error, print_info
from ..utils.project_info import has_dependency
from ..utils.project_files import (
    copy_template_files,
    is_project_exists_or_raise,
    get_project_path,
    get_packages_url_path,
    get_packages_settings_path,
)

app = typer.Typer(no_args_is_help=True)

@app.command()
def install():
    """
    Install and configure {package-display-name}
    """
    is_project_exists_or_raise()

    # Check for dependencies (if needed)
    # print_step("Checking if required-package is installed ...")
    # if not has_dependency("required-package"):
    #     print_error("'required-package' is not installed. Please install it first.")
    #     print_info("\n> ddx packages required-package install")
    #     raise typer.Exit(1)

    print_step("Installing {package-name} package ...")

    # Install via uv - adjust as needed:
    # For dev dependencies: ["uv", "add", "{package-name}", "--dev"]
    # For extras: ["uv", "add", "{package-name}[extra]"]
    subprocess.check_call(["uv", "add", "{package-name}"])

    # Copy template files (settings, urls, etc.)
    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir.parent / "templates" / "{template-folder-name}"
    project_dir = get_project_path()

    copy_template_files(
        source_dir=source_dir,
        dest_dir=project_dir,
        template_context={}  # Add context dict if using Jinja2 templates
    )

    print_success("{package-display-name} is installed successfully.")

@app.command()
def remove():
    """
    Remove {package-display-name}
    """
    print_step("Removing {package-name} package ...")

    # Remove package if installed
    if has_dependency("{package-name}"):
        # For dev dependencies: ["uv", "remove", "{package-name}", "--group", "dev"]
        subprocess.check_call(["uv", "remove", "{package-name}"])

    # Remove generated URL file (if exists)
    url_path = Path.joinpath(get_packages_url_path(), "{package_name}.py")
    url_path.unlink(missing_ok=True)

    # Remove generated settings file (if exists)
    settings_path = Path.joinpath(get_packages_settings_path(), "{package_name}.py")
    settings_path.unlink(missing_ok=True)

    print_success("{package-display-name} is removed successfully.")

# Add env() command only if secrets/user-specific config needed
# @app.command()
# def env():
#     """
#     Configure environment variables for {package-display-name}
#     """
#     # See Step 1.4 for implementation
```

**For Multi-Action Packages:**

Create directory structure and files as shown in `django_storages` example. The `__init__.py` combines sub-apps, `install.py` has variant-specific installs, `remove.py` handles cleanup, `env.py` manages environment variables per variant.

Always look at existing multi-action packages for reference such as `django_storages folder`.

#### Step 1.4: Implement Environment Variable Management (if needed)

**Only create `env()` command if the package requires:**
- API keys, tokens, passwords (secrets)
- User-specific identifiers (bucket names, project IDs, etc.)

**Pattern for Single-Action Package** (add to same file):

```python
from typing_extensions import Annotated
from ..utils.project_files import add_env_varibles

@app.command()
def env(
    api_key: Annotated[
        str,
        typer.Option(
            help="The API key for authentication",
            prompt="Please enter the API key",
            hide_input=True,  # Use for secrets
        ),
    ],
    config_value: Annotated[
        str,
        typer.Option(
            help="Configuration value description",
            prompt="Please enter the configuration value",
        ),
    ],
):
    """
    Configure environment variables for {package-name}
    """
    is_project_exists_or_raise()

    print_step("Configuring environment variables for {package-name} ...")

    add_env_varibles(key="PACKAGE_API_KEY", value=api_key)
    add_env_varibles(key="PACKAGE_CONFIG_VALUE", value=config_value)

    print_success("{package-name} environment variables configured successfully.")
```

**Pattern for Multi-Action Package** (separate `env.py` file):

Create `djdevx/packages/{package_name}/env.py` with separate commands per variant (see `django_storages/env.py` for reference).

**Key principles:**
- Use `hide_input=True` for secrets (passwords, keys, tokens)
- Use descriptive prompts and help text
- Variable names should follow pattern: `PACKAGENAME_SETTING_NAME`
- Always call `is_project_exists_or_raise()` at the start

#### Step 1.5: Register Package in Main Init File

Edit `djdevx/packages/__init__.py`:

1. **Import the package** at the top (maintain alphabetical order):
```python
from .{package_name} import app as {package_alias}
```

2. **Register with main app** (maintain alphabetical order by CLI name):
```python
app.add_typer(
    {package_alias},
    name="{cli-package-name}",  # Use official package name with hyphens
    help="Manage {package-display-name} package",
)
```

**Example:**
```python
# At imports (alphabetical)
from .django_cors_headers import app as cors

# In registrations (alphabetical by name)
app.add_typer(
    cors,
    name="django-cors-headers",
    help="Manage django-cors-headers package",
)
```

#### Step 1.6: Create Settings Template

**Determine file naming:**
- **Static settings** (no Jinja2): `templates/{package-name}/settings/packages/{package_name}.py`
- **Templated settings** (uses Jinja2): `templates/{package-name}/settings/packages/{package_name}.py.j2`

**Create the settings file with:**

```python
# Import statements needed for configuration

# Add to INSTALLED_APPS (if required)
INSTALLED_APPS = [
    "{package.app.path}",
]

# Middleware (if required)
MIDDLEWARE = [
    "{package.middleware.path}",
]

# Package-specific settings
PACKAGE_SETTING = "value"

# For environment variables with secure defaults:
from settings.utils.env import get_env
env = get_env()

PACKAGE_SECRET = env("PACKAGE_SECRET", default="")
PACKAGE_URL = env("PACKAGE_URL", default="http://localhost:8000")
```

**For Jinja2 templates** (`.py.j2` extension):

```python
{% if variant_flag %}
# Variant-specific configuration
SETTING = "variant-value"
{% endif %}

# Use template context from copy_template_files(template_context={...})
```

**Best practices:**
- Import `env` helper for environment variables: `from settings.utils.env import get_env`
- Use `default=""` for required secrets (forces user to set via env command)
- Use sensible defaults for non-secret settings
- Comment complex configurations
- Follow Django's official documentation exactly

#### Step 1.7: Create URL Configuration (if needed)

**Only create URLs if the package exposes views/endpoints.**

**Determine file naming:**
- **Static URLs**: `templates/{package-name}/urls/packages/{package_name}.py`
- **Templated URLs**: `templates/{package-name}/urls/packages/{package_name}.py.j2`

**Create the URL file:**

```python
from django.urls import path, include

urlpatterns = [
    path("{url-prefix}/", include("{package.urls}")),
]
```

**For packages with multiple URL patterns:**

```python
from django.urls import path
from {package} import views

urlpatterns = [
    path("endpoint1/", views.view1, name="{package}-endpoint1"),
    path("endpoint2/", views.view2, name="{package}-endpoint2"),
]
```

**Best practices:**
- Use descriptive URL prefixes
- Follow package documentation for URL patterns exactly
- Include namespace if package recommends it
- Template dynamic parts with Jinja2 if needed

#### Step 1.8: Create Additional Template Files (if needed)

Some packages require additional files beyond settings/URLs:

**Static files** (CSS, JS):
- Create in `templates/{package-name}/static/` matching Django's structure
- Will be copied to project during installation

**Custom app files** (authentication backends, signals):
- Create in `templates/{package-name}/authentication/` or appropriate folder
- These extend package functionality

**Application configurations**:
- For Channels: `templates/{package-name}/applications/`
- For WebSocket routing: `templates/{package-name}/ws_urls/`

**Pattern:** Match Django's expected directory structure for auto-discovery.

#### Step 1.9: Test the Integration

**Manual testing checklist:**

1. **Test install command:**
   ```bash
   ddx packages {package-name} install
   ```
   - Verify package installed via `uv pip list`
   - Check settings file created in correct location
   - Check URL file created (if applicable)
   - Verify no errors during template copying

2. **Test env command (if exists):**
   ```bash
   ddx packages {package-name} env
   ```
   - Verify prompts work correctly
   - Check `.env` file contains correct variables
   - Test with invalid inputs

3. **Test remove command:**
   ```bash
   ddx packages {package-name} remove
   ```
   - Verify package uninstalled
   - Verify settings file removed
   - Verify URL file removed
   - No orphaned files remain

4. **Test in actual Django project:**
   - Run `python manage.py check`
   - Run migrations if needed
   - Test package functionality works
   - Verify settings take effect

#### Step 1.10: Common Patterns and Examples

**Package with dependencies:**
```python
# In install() command
print_step("Checking if djangorestframework is installed ...")
if not has_dependency("djangorestframework"):
    print_error("'djangorestframework' package is not installed. Please install that package first.")
    print_info("\n> ddx packages djangorestframework install")
    raise typer.Exit(1)
```

**Package with extras:**
```python
subprocess.check_call(["uv", "add", "drf-spectacular[sidecar]"])
```

**Dev-only package:**
```python
# Install
subprocess.check_call(["uv", "add", "django-debug-toolbar", "--group", "dev"])

# Remove
subprocess.check_call(["uv", "remove", "django-debug-toolbar", "--group", "dev"])
```

**Multi-backend package structure** (like django-storages):
- Each backend is a separate `install` subcommand
- Shared `remove` command handles all variants
- Separate `env` commands per backend
- Use Jinja2 flags in templates: `{% if isS3 %}...{% endif %}`

**Template context passing:**
```python
# In install command
copy_template_files(
    source_dir=source_dir,
    dest_dir=project_dir,
    template_context={
        "isS3": True,
        "use_feature": user_choice,
    }
)

# In template (.j2 file)
{% if isS3 %}
BACKEND = "storages.backends.s3.S3Storage"
{% endif %}
```

---

### Key Principles for Package Integration

1. **Always research first** - Search official docs before writing code
2. **Security by default** - Secrets via env vars, secure defaults for all settings
3. **Follow conventions** - Alphabetical ordering, naming patterns, file locations
4. **Idempotent operations** - Install/remove should be safely repeatable
5. **Clear user feedback** - Use print_step, print_success, print_error consistently
6. **Dependency management** - Check and install dependencies in correct order
7. **Template correctly** - Use Jinja2 only when needed, plain Python otherwise
8. **Clean removal** - Remove ALL traces of package in remove command
9. **Test thoroughly** - Manual testing checklist before considering done
10. **Document behavior** - Clear docstrings for all commands
