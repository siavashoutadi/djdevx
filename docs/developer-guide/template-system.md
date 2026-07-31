# Template System

The template system manages Jinja2 template files that are rendered at install
time and optionally restored at remove time. It is implemented by the
`Scaffold` class in `djdevx/utils/scaffold.py`.

## Directory Structure

Templates are stored within each installable's package directory:

```
djdevx/
  packages/
    whitenoise/
      templates/                 ← Jinja2 templates
        apps.py.jinja2
        settings.py.jinja2
    django_allauth/
      templates/
        account/
          apps.py.jinja2
          settings.py.jinja2
        mfa/
          apps.py.jinja2
  features/
    pwa/
      templates/
        manifest.json.jinja2
  frameworks/
    bootstrap/
      (no templates - CSS/JS only)
  database/
    postgres/
      templates/
        docker_config.py.jinja2
```

## Template Engine

Templates use Jinja2 with Django-like syntax (`{{ }}`, `{% %}`).

### Context Variables

Variables available in all templates:

| Variable | Source | Description |
|----------|--------|-------------|
| `project_name` | `[tool.djdevx].project_name` | Django project name |
| `package_name` | `Installable.name` | Installable identifier |
| `app_name` | Inferred from project | Default Django app |
| `secret_key` | Auto-generated | Random 64-char key |
| `<InstallParam>` | CLI prompts | User-provided values |

### Template Example

```
{# packages/whitenoise/templates/apps.py.jinja2 #}
INSTALLED_APPS.append("whitenoise.runserver_nostatic")
```

```
{# packages/allauth/templates/account/settings.py.jinja2 #}
# {{ project_name }} settings
ACCOUNT_EMAIL_SUBJECT_PREFIX = "{{ email_subject_prefix }}"
```

## Scaffold (formerly TemplateManager)

`Scaffold` (`djdevx/utils/scaffold.py`) handles the full lifecycle:

| Method | Description |
|--------|-------------|
| `copy_templates(installable, variant)` | Renders Jinja2 templates to project, saves originals for restore |
| `cleanup_files(installable)` | Removes generated files listed in `files_to_remove` |
| `restore_originals(installable)` | Restores originals saved during `copy_templates` |
| `copy_templates_for_tracking(installable, variant)` | Copies `post_install` tracking files |

### Original File Backup

Before overwriting an existing file, `copy_templates` saves a copy with a
`.orig` extension in a tracking directory. These are used by
`restore_originals` when the installable is removed:

```
.project/
  ddx/
    originals/
      <installable_name>/
        settings/django/installed_apps.py.orig
```

## installable_refs.json

The template that generates the list of installable refs is stored at:

```
files/installable_refs.json.jinja2
```

This template gets rendered into the project's `.project/ddx/` directory
and is used by the resolution system.

## Template Discovery

Templates are found relative to the installable's module directory under a
`templates/` folder. If a variant specifies a `template_path`, that subfolder
is used instead:

```
templates/account/  → variant template_path="account"
templates/mfa/      → variant template_path="mfa"
```

## Restore on Remove

The `restore_on_remove` dict on an `InstallableConfig` maps destination paths
to originals that should be restored when the installable is removed:

```python
restore_on_remove: dict[str, str] = {
    "settings/django/sessions.py": "settings/django/sessions.py"
}
```

## Related

- [Installable System](installable-system.md) — Lifecycle hooks
- [Creating an Installable](creating-an-installable.md) — Template creation guide
- [Add a Package](adding-a-package.md) — Package template conventions
