# djdevx Contributor Guide

## Table of Contents
1. [Adding New Package Templates](#adding-new-package-templates)
2. [Template Integration with CLI Commands](#template-integration-with-cli-commands)
3. [Generated Code Lifecycle](#generated-code-lifecycle)
4. [Development Workflow](#development-workflow)
5. [Testing Your Changes](#testing-your-changes)

## Adding New Package Templates

This guide walks you through adding support for a new Django package to djdevx. We'll use `django-extensions` as an example.

### Step 1: Create Package Template Structure

Create the template directory structure:

```bash
mkdir -p djdevx/templates/django-extensions/settings/packages
```

**Template Structure**:
```
djdevx/templates/django-extensions/
├── settings/
│   └── packages/
│       └── django_extensions.py
└── urls/                           # Optional: if package needs URLs
    └── packages/
        └── django_extensions.py
```

### Step 2: Create Package Settings Template

Create `djdevx/templates/django-extensions/settings/packages/django_extensions.py`:

```python
from settings import INSTALLED_APPS
from settings.django.base import DEBUG
from settings.utils.env import get_env

env = get_env()

INSTALLED_APPS += [
    "django_extensions",
]

# Package-specific settings
if DEBUG:
    # Development-only configurations
    SHELL_PLUS_PRINT_SQL = True
    SHELL_PLUS_PRINT_SQL_TRUNCATE = 1000

# Environment-based configurations
GRAPH_MODELS = {
    'all_applications': True,
    'group_models': True,
}
```

**Key Patterns for Settings Templates**:

1. **Import Required Modules**:
   ```python
   from settings import INSTALLED_APPS, MIDDLEWARE  # For list modifications
   from settings.django.base import DEBUG           # For conditional logic
   from settings.utils.env import get_env          # For environment variables
   ```

2. **Modify Django Lists**:
   ```python
   # Add to end of list
   INSTALLED_APPS += ["package_name"]

   # Insert at specific position
   MIDDLEWARE.insert(0, "package.middleware.SomeMiddleware")

   # Conditional additions
   if DEBUG:
       INSTALLED_APPS += ["debug_package"]
   ```

3. **Environment Variables**:
   ```python
   env = get_env()
   PACKAGE_SETTING = env("PACKAGE_SETTING", default="default_value")
   PACKAGE_LIST = env.list("PACKAGE_LIST", default=[])
   PACKAGE_BOOL = env.bool("PACKAGE_BOOL", default=False)
   ```

### Step 3: Create Package URLs Template (Optional)

If your package needs URL patterns, create `djdevx/templates/django-extensions/urls/packages/django_extensions.py`:

```python
from django.urls import path, include
from settings.django.base import DEBUG

urlpatterns = []

if DEBUG:
    # Only include URLs in debug mode
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
```

### Step 4: Create CLI Command Module

Create `djdevx/packages/django_extensions.py`:

```python
import subprocess
import typer

from pathlib import Path

from ..utils.print_console import print_step, print_success
from ..utils.project_info import has_dependency
from ..utils.project_files import (
    copy_template_files,
    is_project_exists_or_raise,
    get_project_path,
    get_packages_url_path,
    get_packages_settings_path,
    add_env_varibles,
    remove_env_varibles,
)

app = typer.Typer(no_args_is_help=True)


@app.command()
def install():
    """
    Install and configure django-extensions
    """
    is_project_exists_or_raise()

    print_step("Installing django-extensions package ...")
    subprocess.check_call(["uv", "add", "django-extensions"])

    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir.parent / "templates" / "django-extensions"
    project_dir = get_project_path()

    copy_template_files(
        source_dir=source_dir, dest_dir=project_dir, template_context={}
    )

    print_success("django-extensions is installed successfully.")


@app.command()
def remove():
    """
    Remove django-extensions package
    """
    print_step("Removing django-extensions package ...")

    if has_dependency("django-extensions"):
        subprocess.check_call(["uv", "remove", "django-extensions"])

    # Remove generated settings file
    settings_path = Path.joinpath(get_packages_settings_path(), "django_extensions.py")
    settings_path.unlink(missing_ok=True)

    # Remove generated URLs file (if exists)
    url_path = Path.joinpath(get_packages_url_path(), "django_extensions.py")
    url_path.unlink(missing_ok=True)

    print_success("django-extensions is removed successfully.")


@app.command()
def env():
    """
    Configure environment variables for django-extensions
    """
    is_project_exists_or_raise()

    print_step("Creating environment variables for django-extensions ...")
    add_env_varibles(
        key="DJANGO_EXTENSIONS_SETTING",
        value="production_value",
    )

    print_success("django-extensions environment variables are configured successfully.")


if __name__ == "__main__":
    app()
```

**CLI Command Patterns**:

1. **Basic Package** (settings only):
   - `install()`: Install package + copy templates
   - `remove()`: Remove package + clean up files

2. **Complex Package** (settings + URLs + environment):
   - `install()`: Install + copy templates + configure environment
   - `remove()`: Remove + clean up all files + remove environment variables
   - `env()`: Configure environment variables separately

3. **Package with Dependencies**:
   ```python
   @app.command()
   def install():
       # Install multiple related packages
       subprocess.check_call(["uv", "add", "main-package", "helper-package"])
       subprocess.check_call(["uv", "add", "dev-package", "--group", "dev"])
   ```

### Step 5: Register CLI Command

Add your new package to `djdevx/packages/__init__.py`:

```python
from .django_extensions import app as django_extensions

app.add_typer(
    django_extensions,
    name="django-extensions",
    help="Manage django-extensions package",
)
```

### Step 6: Handle Complex Package Scenarios

#### Packages with Custom Template Context

Some packages need dynamic template variables:

```python
@app.command()
def install(
    api_key: str = typer.Option(..., prompt="Enter your API key")
):
    template_context = {
        "api_key": api_key,
        "package_name": "my-package"
    }

    copy_template_files(
        source_dir=source_dir,
        dest_dir=project_dir,
        template_context=template_context
    )
```

Template usage:
```python
# In settings template
API_KEY = "{{ api_key }}"
PACKAGE_NAME = "{{ package_name }}"
```

#### Packages that Modify Existing Files

Some packages need to modify existing files (like ASGI applications):

```python
@app.command()
def install():
    # ... install package ...

    # Replace ASGI application
    current_dir = Path(__file__).resolve().parent
    source_file = current_dir.parent / "templates" / "my-package" / "applications" / "asgi.py"
    project_dir = get_project_path() / "applications"

    copy_template_file(
        source_file=source_file,
        dest_dir=project_dir,
        template_context={}
    )
```

#### Packages with WebSocket Support

For packages that add WebSocket functionality:

```python
from ..utils.project_files import get_ws_url_path

@app.command()
def remove():
    # ... remove package ...

    # Clean up WebSocket URLs
    ws_url_path = get_ws_url_path()
    if ws_url_path.exists():
        shutil.rmtree(ws_url_path)
```

Create WebSocket URL template at `djdevx/templates/my-package/ws_urls/my_package.py`:

```python
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/my-feature/", consumers.MyConsumer.as_asgi()),
]
```

## Template Integration with CLI Commands

### Template Context Variables

Templates receive context variables from CLI commands. Here are the common patterns:

#### Project Initialization Context

```python
# In djdevx/init.py
data = {
    "project_name": project_name,
    "project_description": project_description,
    "django_secret_key": generate_secret(),
    "python_version": python_version,
}
```

#### App Creation Context

```python
# In djdevx/create/app.py
template_context = {
    "application_name": application_name
}
```

#### Feature Addition Context

```python
# In djdevx/feature/pwa.py
template_context = {
    "name": name,
    "short_name": short_name,
    "description": description,
    "background_color": background_color,
    # ... more PWA-specific variables
}
```

### Template Processing Pipeline

The template processing follows this pipeline:

1. **Path Template Processing**: Directory and file names can contain Jinja2 variables
   ```
   templates/{{application_name}}/models.py.j2
   → myapp/models.py
   ```

2. **Content Template Processing**: File contents are processed through Jinja2
   ```jinja2
   class {{model_name}}(models.Model):
       name = models.CharField(max_length={{max_length}})
   ```

3. **Extension Handling**: `.j2` files are processed and extension is removed
   ```
   settings.py.j2 → settings.py (processed)
   static.css → static.css (copied as-is)
   ```

### Advanced Template Techniques

#### Conditional File Generation

```jinja2
{% if include_api %}
from rest_framework import serializers

class {{model_name}}Serializer(serializers.ModelSerializer):
    class Meta:
        model = {{model_name}}
        fields = '__all__'
{% endif %}
```

#### Dynamic List Generation

```jinja2
INSTALLED_APPS += [
{% for app in additional_apps %}
    "{{ app }}",
{% endfor %}
]
```

#### Environment-Aware Templates

```jinja2
{% if environment == "development" %}
DEBUG = True
ALLOWED_HOSTS = ['*']
{% else %}
DEBUG = False
ALLOWED_HOSTS = {{ allowed_hosts | tojson }}
{% endif %}
```

## Generated Code Lifecycle

### Phase 1: Template Creation
1. Developer creates template files in `djdevx/templates/{package-name}/`
2. Templates use Jinja2 syntax for dynamic content
3. Templates follow the isolation pattern (settings/packages/, urls/packages/)

### Phase 2: CLI Command Processing
1. User runs CLI command (e.g., `djdevx packages django-cors-headers install`)
2. CLI command validates project exists
3. Package dependencies are installed via `uv`
4. Template context is prepared

### Phase 3: Template Rendering
1. `copy_template_files()` processes template directory
2. Jinja2 renders `.j2` files with provided context
3. Static files are copied as-is
4. Generated files are placed in target project

### Phase 4: Django Integration
1. Settings auto-discovery loads new package settings
2. URL auto-discovery includes new package URLs
3. Django application starts with new configuration

### Phase 5: Package Removal (Optional)
1. User runs remove command
2. Python package is uninstalled
3. Generated files are deleted
4. Environment variables are cleaned up

## Development Workflow

### Setting Up Development Environment

1. **Clone the repository**:
   ```bash
   git clone https://github.com/siavashoutadi/djdevx.git
   cd djdevx
   ```

2. **Install development dependencies**:
   ```bash
   uv sync --dev
   ```

3. **Install djdevx in development mode**:
   ```bash
   uv pip install -e .
   ```

### Testing Your Package Addition

1. **Create a test project**:
   ```bash
   mkdir test-project
   cd test-project
   djdevx init --project-name "test" --project-description "Test project"
   ```

2. **Test package installation**:
   ```bash
   djdevx packages your-new-package install
   ```

3. **Verify generated files**:
   ```bash
   # Check settings file was created
   ls settings/packages/your_new_package.py

   # Check URLs file was created (if applicable)
   ls urls/packages/your_new_package.py

   # Test Django can load the settings
   uv run manage.py check
   ```

4. **Test package removal**:
   ```bash
   djdevx packages your-new-package remove

   # Verify files were cleaned up
   ls settings/packages/  # Should not contain your package
   ```

### Code Quality Standards

1. **Follow existing patterns**: Look at similar packages for consistency
2. **Use type hints**: All functions should have proper type annotations
3. **Add docstrings**: Document all CLI commands and functions
4. **Handle errors gracefully**: Use `is_project_exists_or_raise()` and proper error handling
5. **Clean up on removal**: Ensure `remove()` command cleans up all generated files

### Template Best Practices

1. **Use meaningful variable names**: `{{ api_key }}` not `{{ key }}`
2. **Provide sensible defaults**: Use `env("SETTING", default="default_value")`
3. **Conditional configurations**: Use `{% if DEBUG %}` for development-only settings
4. **Import at the top**: Keep all imports at the beginning of template files
5. **Comment complex logic**: Explain non-obvious template logic

## Testing Your Changes

### Manual Testing Checklist

- [ ] Package installs without errors
- [ ] Generated settings file is syntactically correct
- [ ] Django project starts successfully (`uv run manage.py runserver`)
- [ ] Package functionality works as expected
- [ ] Package removes cleanly without leaving files
- [ ] Environment variables are handled correctly
- [ ] URLs are accessible (if package adds URLs)

### Automated Testing

Create test cases for your package:

```python
# tests/test_your_package.py
import pytest
from pathlib import Path
from djdevx.packages.your_package import install, remove

def test_package_install(tmp_path):
    # Test installation logic
    pass

def test_package_remove(tmp_path):
    # Test removal logic
    pass
```

### Integration Testing

Test the complete workflow:

```bash
# Create fresh project
djdevx init --project-name "integration-test"

# Install your package
djdevx packages your-package install

# Verify Django works
uv run manage.py check
uv run manage.py migrate
uv run manage.py collectstatic --noinput

# Test package functionality
# ... package-specific tests ...

# Remove package
djdevx packages your-package remove

# Verify cleanup
uv run manage.py check
```

## Common Patterns and Examples

### Simple Package (Settings Only)

**Example**: `django-humanize`

Template: `djdevx/templates/django-humanize/settings/packages/django_humanize.py`
```python
from settings import INSTALLED_APPS

INSTALLED_APPS += [
    "django.contrib.humanize",
]
```

CLI: `djdevx/packages/django_humanize.py`
```python
@app.command()
def install():
    subprocess.check_call(["uv", "add", "django"])  # Already included
    copy_template_files(source_dir=source_dir, dest_dir=project_dir, template_context={})
```

### Package with URLs

**Example**: `django-debug-toolbar`

Settings Template:
```python
from settings import INSTALLED_APPS, MIDDLEWARE
from settings.django.base import DEBUG

if DEBUG:
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

    INTERNAL_IPS = ["127.0.0.1"]
```

URLs Template:
```python
from django.urls import path, include
from settings.django.base import DEBUG

urlpatterns = []

if DEBUG:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
```

### Package with Environment Variables

**Example**: `django-storages` (AWS S3)

Settings Template:
```python
from settings.utils.env import get_env

env = get_env()

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default="us-east-1")

DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
STATICFILES_STORAGE = "storages.backends.s3boto3.StaticS3Boto3Storage"
```

CLI Command:
```python
@app.command()
def env():
    add_env_varibles("AWS_ACCESS_KEY_ID", "your-access-key")
    add_env_varibles("AWS_SECRET_ACCESS_KEY", "your-secret-key")
    add_env_varibles("AWS_STORAGE_BUCKET_NAME", "your-bucket-name")
```
