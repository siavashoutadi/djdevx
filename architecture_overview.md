# djdevx Architecture Overview

## Executive Summary

`djdevx` is a sophisticated Django project scaffolding system built on **Typer CLI** and **Jinja2 templating**. It implements a modular architecture where each Django package gets isolated configuration files, enabling clean separation of concerns and easy package management.

## Core Architecture Components

### 1. CLI Command Structure (Typer-based)

The CLI follows a hierarchical command structure using Typer:

```
djdevx/
├── main.py              # Root CLI app with sub-commands
├── init.py              # Project initialization
├── packages/            # Package management commands
├── create/              # Django app creation
├── feature/             # Feature addition (PWA, etc.)
├── requirement.py       # Dependency checking
└── version.py           # Version display
```

**Main CLI Entry Point** (`djdevx/main.py`):
```python
app = typer.Typer(no_args_is_help=True)

app.add_typer(version_app)
app.add_typer(requirement_app)
app.add_typer(init_app)
app.add_typer(packages_app, name="packages", help="Install and configure django packages")
app.add_typer(feature_app, name="feature", help="Add features to your project")
app.add_typer(create_app, name="create", help="Create new Django applications or components")
```

### 2. Template System Architecture

**Jinja2 Template Processing** (`djdevx/utils/django/project_manager.py`):

The system uses a sophisticated template processing pipeline:

```python
def copy_template_files(source_dir: Path, dest_dir: Path, template_context: dict):
    dest_dir.mkdir(parents=True, exist_ok=True)
    jinja_env = Environment(loader=FileSystemLoader(source_dir))

    for source_path in source_dir.rglob("*"):
        rel_path = source_path.relative_to(source_dir)

        # Template path names themselves
        rendered_parts = [
            render_template_string(part, template_context) for part in rel_path.parts
        ]
        dest_path = dest_dir / Path(*rendered_parts)

        if source_path.suffix == ".j2":
            # Process Jinja2 templates
            template = jinja_env.get_template(str(rel_path))
            rendered_content = template.render(**template_context)
            dest_path = dest_path.with_suffix("")  # Remove .j2 extension
            dest_path.write_text(rendered_content)
        else:
            # Copy static files
            shutil.copy2(source_path, dest_path)
```

**Template Context Variables**:
- `project_name`: User-provided project name
- `project_description`: Project description
- `django_secret_key`: Auto-generated secret key
- `python_version`: Target Python version
- Package-specific variables (e.g., `application_name` for app creation)

### 3. Package Isolation Strategy

Each Django package follows a strict isolation pattern:

```
djdevx/templates/{package-name}/
├── settings/
│   └── packages/
│       └── {package_name}.py     # Package-specific Django settings
├── urls/
│   └── packages/
│       └── {package_name}.py     # Package-specific URL patterns
└── ws_urls/                      # WebSocket URLs (for packages like channels)
    └── {package_name}.py
```

**Example: django-cors-headers Package Structure**:

Template Location: `djdevx/templates/django-cors-headers/`
```
settings/
└── packages/
    └── django_cors_headers.py
```

Generated Settings File:
```python
from settings import INSTALLED_APPS, MIDDLEWARE
from settings.django.base import DEBUG
from settings.utils.env import get_env

INSTALLED_APPS += [
    "corsheaders",
]

MIDDLEWARE.insert(0, "corsheaders.middleware.CorsMiddleware")

env = get_env()

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS", default=[])
    CORS_ALLOWED_ORIGIN_REGEXES = env("CORS_ALLOWED_ORIGIN_REGEXES", default=[])
```

### 4. Generated Django Project Structure

The final Django project follows this structure:

```
my-project/
├── pyproject.toml                    # Generated from template with project variables
├── manage.py                         # Standard Django management script
├── Dockerfile                        # Generated from Dockerfile.j2 template
├── settings/
│   ├── __init__.py                   # Auto-imports all settings modules
│   ├── django/                       # Core Django settings
│   │   ├── base.py                   # Base Django configuration
│   │   ├── database.py               # Database configuration
│   │   └── email.py                  # Email configuration
│   ├── packages/                     # Package-specific settings
│   │   ├── __init__.py
│   │   ├── django_cors_headers.py    # Added when installing django-cors-headers
│   │   └── channels.py               # Added when installing channels
│   ├── apps/                         # App-specific settings
│   └── utils/
│       └── env.py                    # Environment variable handling
├── urls/
│   ├── __init__.py                   # Auto-imports all URL modules
│   ├── django/
│   │   └── admin.py                  # Django admin URLs
│   ├── packages/                     # Package-specific URLs
│   │   └── djangorestframework.py   # DRF URLs (if installed)
│   └── apps/                         # App-specific URLs
├── ws_urls/                          # WebSocket URLs (created by channels)
│   ├── __init__.py                   # Auto-imports WebSocket patterns
│   └── packages/
├── applications/
│   ├── wsgi.py                       # WSGI application
│   └── asgi.py                       # ASGI application (modified by channels)
├── users/                            # Default user app
├── templates/                        # Django templates
└── static/                           # Static files
```

## Execution Flow: CLI Command → Template Rendering → Django Files

### 1. Project Initialization Flow

```
djdevx init --project-name "myproject" --project-description "My awesome project"
    ↓
init.py:init() function
    ↓
Template context creation:
{
    "project_name": "myproject",
    "project_description": "My awesome project",
    "django_secret_key": "auto-generated-secret",
    "python_version": "3.13"
}
    ↓
copy_template_files(source_dir="djdevx/templates/init", dest_dir=".", template_context=data)
    ↓
Jinja2 processes all .j2 files:
- pyproject.toml.j2 → pyproject.toml (with project variables)
- Dockerfile.j2 → Dockerfile (with Python version)
- settings/utils/env.py.j2 → settings/utils/env.py (with project name)
    ↓
Install base dependencies via uv
    ↓
Initialize git repository
```

### 2. Package Installation Flow

```
djdevx packages django-cors-headers install
    ↓
django_cors_headers.py:install() function
    ↓
uv = UvRunner()
uv.add_package("django-cors-headers")
    ↓
copy_template_files(
    source_dir="djdevx/templates/django-cors-headers",
    dest_dir=project_path,
    template_context={}
)
    ↓
Creates: settings/packages/django_cors_headers.py
    ↓
Django settings auto-discovery loads the new package settings
```

### 3. Settings Auto-Discovery Mechanism

**Main Settings Loader** (`settings/__init__.py`):
```python
import glob
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SETTINGS_DIR = BASE_DIR / "settings"

DJANGO_SETTINGS_DIR = SETTINGS_DIR / "django"
PACKAGES_SETTINGS_DIR = SETTINGS_DIR / "packages"
APPS_SETTINGS_DIR = SETTINGS_DIR / "apps"

setting_files = []
setting_files += glob.glob(str(DJANGO_SETTINGS_DIR / "[!__init__]*.py"))
setting_files += glob.glob(str(PACKAGES_SETTINGS_DIR / "[!__init__]*.py"))
setting_files += glob.glob(str(APPS_SETTINGS_DIR / "[!__init__]*.py"))

# Execute all settings files in the current namespace
for setting_file in setting_files:
    with open(setting_file) as f:
        code = compile(f.read(), setting_file, "exec")
        exec(code)
```

### 4. URL Auto-Discovery Mechanism

**Main URL Loader** (`urls/__init__.py`):
```python
import importlib
from pathlib import Path

URLS_DIR = Path(__file__).parent
url_files = [str(f) for f in Path(URLS_DIR).rglob("*.py") if f.name != "__init__.py"]

urlpatterns = []

for file_path in url_files:
    relative_path = Path(file_path).relative_to(URLS_DIR).with_suffix("")
    module_name = f"urls.{'.'.join(relative_path.parts)}"

    try:
        module = importlib.import_module(module_name)
        if hasattr(module, "urlpatterns"):
            urlpatterns += module.urlpatterns
    except Exception as e:
        print(f"Error importing {module_name}: {e}")
```

## Environment Variable Management

**Environment Detection** (`settings/utils/env.py`):
```python
def get_env():
    env = environ.Env()
    if is_local():
        environ.Env.read_env(LOCAL_ENV_FILE)  # .environments/dev
    elif is_swarm():
        environ.Env.read_env(SWARM_ENV_FILE)  # Docker Swarm secrets
    return env

def is_local():
    return os.path.exists(LOCAL_ENV_FILE) and not is_docker()

def is_docker():
    return os.path.exists("/.dockerenv")
```

**Environment Variable Distribution**:
- **Local Development**: `.environments/dev` file
- **Docker**: Environment variables passed to container
- **Docker Swarm**: Secrets mounted at `/run/secrets/{project-name}-secret`

## Package-Specific Features

### Complex Package Example: Channels (WebSocket Support)

**Installation Process**:
1. Install Python packages: `channels[daphne]`, `channels_redis`
2. Copy template files to project
3. Create WebSocket URL structure
4. Replace ASGI application with channels-aware version
5. Add environment variables for Redis connection

**Generated Files**:
- `settings/packages/channels.py` - Channel layers configuration
- `ws_urls/__init__.py` - WebSocket URL auto-discovery
- `applications/asgi.py` - Channels-enabled ASGI application

**ASGI Application Transformation**:

Before (Standard Django):
```python
from django.core.asgi import get_asgi_application
application = get_asgi_application()
```

After (Channels-enabled):
```python
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from ws_urls import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
})
```

## Key Design Principles

1. **Modular Configuration**: Each package manages its own settings and URLs
2. **Auto-Discovery**: Settings and URLs are automatically loaded without manual imports
3. **Environment Awareness**: Different configurations for local, Docker, and production
4. **Template-Driven**: All generated code comes from Jinja2 templates
5. **Dependency Management**: Uses `uv` for fast Python package management
6. **Clean Removal**: Packages can be cleanly removed with all their configurations

## Template System Mechanics

### Template File Processing Rules

1. **`.j2` files**: Processed through Jinja2 template engine, extension removed
2. **Regular files**: Copied as-is to destination
3. **Directory names**: Can contain Jinja2 variables (e.g., `{{application_name}}/`)
4. **File names**: Can contain Jinja2 variables in the name itself

### Custom Template Functions

The system provides several utility functions for templates:
- Environment variable access via `get_env()`
- Conditional rendering based on `DEBUG` mode
- Dynamic list manipulation (e.g., `INSTALLED_APPS += [...]`)

This architecture enables djdevx to provide a clean, maintainable, and extensible Django project scaffolding system that scales from simple projects to complex applications with multiple third-party packages.
