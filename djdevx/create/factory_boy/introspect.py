"""Introspect Django models of the generated project via ``manage.py shell``."""

import json

from djdevx.utils.django.manage_commands import ManageCommands


class IntrospectionError(RuntimeError):
    """Raised when the models of the Django project cannot be introspected."""


_SNIPPET = r"""
import json

from django.apps import apps


def _related_ref(field):
    related = field.related_model
    if related is None:
        return None
    return "%s.%s" % (related._meta.app_label, related.__name__)


def _field_info(field):
    info = {
        "name": field.name,
        "class": field.__class__.__name__,
        "null": bool(field.null),
        "unique": bool(field.unique),
        "primary_key": bool(field.primary_key),
        "max_length": getattr(field, "max_length", None),
        "auto_now": bool(getattr(field, "auto_now", False)),
        "auto_now_add": bool(getattr(field, "auto_now_add", False)),
        "many_to_many": bool(field.many_to_many),
        "one_to_one": bool(field.one_to_one),
        "related": _related_ref(field),
        "choices": [str(value) for value, _ in field.choices] if field.choices else [],
    }
    if info["class"] == "DecimalField":
        info["max_digits"] = field.max_digits
        info["decimal_places"] = field.decimal_places
    return info


def _model_info(model):
    fields = list(model._meta.fields) + list(model._meta.local_many_to_many)
    return {
        "app_label": model._meta.app_label,
        "name": model.__name__,
        "fields": [_field_info(field) for field in fields],
    }


models = []
for app_config in apps.get_app_configs():
    if app_config.name.startswith("django."):
        continue
    for model in app_config.get_models():
        models.append(_model_info(model))

print(json.dumps(models))
"""


def list_models(commands: ManageCommands) -> list[dict]:
    """Return model metadata for every installed (non-Django) app.

    Runs ``manage.py shell -c`` inside the project via the given
    ``ManageCommands`` and parses the JSON printed by the snippet.
    """
    result = commands.run("shell", "-c", _SNIPPET, check=False)
    if result.returncode != 0:
        raise IntrospectionError(
            "Could not introspect your Django models. Make sure the project "
            "environment is installed (run `pixi install` or `ddx dev start`) "
            "and Django can be imported."
        )
    try:
        payload = result.stdout.strip().splitlines()[-1]
        return json.loads(payload)
    except (ValueError, json.JSONDecodeError) as exc:  # noqa: BLE001
        raise IntrospectionError(
            f"Could not parse the model introspection output: {exc}"
        ) from exc
