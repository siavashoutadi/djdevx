"""Map introspected Django model fields to factory-boy/faker declarations."""

import ast
from collections.abc import Callable
from pathlib import Path

BASE_IMPORTS = [
    "import factory",
    "from factory.django import DjangoModelFactory",
]
USER_IMPORT = "from django.contrib.auth import get_user_model"


def _s(value: str) -> str:
    """Render a string literal using double quotes (repo style)."""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _fmt_arg(value) -> str:
    """Render a provider argument as a literal (double-quoted when a string)."""
    return _s(value) if isinstance(value, str) else repr(value)


def _faker(name: str, *args, **kwargs) -> str:
    """Build a ``factory.Faker(...)`` expression from provider + arguments."""
    params = []
    params.extend(_fmt_arg(arg) for arg in args)
    params.extend(f"{key}={_fmt_arg(value)}" for key, value in kwargs.items())
    if params:
        return f'factory.Faker("{name}", {", ".join(params)})'
    return f'factory.Faker("{name}")'


_NAME_FAKER_PROVIDERS = (
    ("email", "email"),
    ("username", "user_name"),
    ("first_name", "first_name"),
    ("last_name", "last_name"),
    ("phone", "phone_number"),
    ("mobile", "phone_number"),
    ("city", "city"),
    ("zip", "postcode"),
    ("postal", "postcode"),
    ("slug", "slug"),
    ("url", "url"),
    ("ip", "ipv4"),
    ("name", "name"),
    ("title", "sentence"),
)


def _provider_for_charfield(field: dict) -> str:
    """Pick a faker provider for a CharField/SlugField by name heuristics."""
    name = field["name"].lower()
    for needle, provider in _NAME_FAKER_PROVIDERS:
        if needle in name:
            return _faker(provider)
    max_length = field.get("max_length")
    if max_length and max_length <= 64:
        return _faker("pystr", max_chars=max_length)
    return _faker("pystr")


def _decimal(field: dict) -> str:
    """Faker provider for a DecimalField using declared digits when available."""
    left = field.get("max_digits")
    right = field.get("decimal_places")
    if left and right is not None:
        return _faker("pydecimal", left_digits=left - right, right_digits=right)
    return _faker("pydecimal", left_digits=5, right_digits=2)


def _rhs_for(field: dict, is_user: bool) -> str | None:
    """Return the right-hand side for a field declaration, or None to skip."""
    class_name = field["class"]
    name = field["name"]

    if field.get("primary_key") or class_name in (
        "AutoField",
        "BigAutoField",
        "SmallAutoField",
    ):
        return None
    if field.get("auto_now") or field.get("auto_now_add"):
        return None

    if is_user and name == "password":
        class_name = "UserPassword"

    if field.get("many_to_many"):
        return "many_to_many"
    if field.get("related"):
        return f'factory.SubFactory("{field["related"]}Factory")'
    if field["choices"]:
        values = ", ".join(_s(choice) for choice in field["choices"])
        return f"factory.Iterator([{values}])"

    optionals: dict[str, Callable[[dict], str]] = {
        "CharField": _provider_for_charfield,
        "SlugField": lambda _field: _faker("slug"),
        "EmailField": lambda _field: _faker("email"),
        "TextField": lambda _field: _faker("paragraph", nb_sentences=3),
        "IntegerField": lambda _field: _faker("random_int", min=0, max=1000),
        "PositiveIntegerField": lambda _field: _faker("random_int", min=0, max=1000),
        "PositiveSmallIntegerField": lambda _field: _faker(
            "random_int", min=0, max=1000
        ),
        "SmallIntegerField": lambda _field: _faker("random_int", min=0, max=1000),
        "BigIntegerField": lambda _field: _faker("random_int", min=0, max=1000000),
        "FloatField": lambda _field: _faker("pyfloat", left_digits=3, right_digits=2),
        "DecimalField": _decimal,
        "UUIDField": lambda _field: _faker("uuid4"),
        "BooleanField": lambda _field: "False",
        "NullBooleanField": lambda _field: "False",
        "DateField": lambda _field: _faker("date_object"),
        "DateTimeField": lambda _field: _faker("date_time"),
        "TimeField": lambda _field: _faker("time_object"),
        "DurationField": lambda _field: _faker("time_delta"),
        "JSONField": lambda _field: _faker(
            "pydict", nb_elements=2, variable_nb_elements=False
        ),
        "GenericIPAddressField": lambda _field: _faker("ipv4"),
        "IPAddressField": lambda _field: _faker("ipv4"),
        "URLField": lambda _field: _faker("url"),
        "FileField": lambda _field: _faker("file_name"),
        "ImageField": lambda _field: _faker("image_url"),
        "UserPassword": lambda _field: (
            'factory.PostGenerationMethodCall("set_password", "password123")'
        ),
    }
    handler = optionals.get(class_name)
    if handler is None:
        return None
    return handler(field)


def _m2m_method(name: str) -> str:
    """Render the ``@factory.post_generation`` method for a M2M field."""
    return (
        f"    @factory.post_generation\n"
        f"    def {name}(self, create, extracted, **kwargs):\n"
        f"        if not create:\n"
        f"            return\n"
        f"        if extracted:\n"
        f"            for item in extracted:\n"
        f"                self.{name}.add(item)"
    )


def _superuser_method() -> str:
    """Render the ``create_superuser`` classmethod for a User factory."""
    return (
        "    @classmethod\n"
        "    def create_superuser(cls, **kwargs):\n"
        "        kwargs.update(\n"
        "            {\n"
        '                "username": "admin",\n'
        '                "email": "admin@example.com",\n'
        '                "password": factory.PostGenerationMethodCall(\n'
        '                    "set_password", "admin@123"\n'
        "                ),\n"
        '                "is_staff": True,\n'
        '                "is_superuser": True,\n'
        "            }\n"
        "        )\n"
        "        return cls.create(**kwargs)"
    )


def build_factory(model_info: dict) -> dict:
    """Build the source body for one factory class.

    Returns a dict with ``class_name``, ``class_body`` (the full indented
    class definition, without trailing newline) and ``imports`` (extra module
    imports the class needs).
    """
    app_label = model_info["app_label"]
    model_name = model_info["name"]
    class_name = f"{model_name}Factory"
    is_user = model_name == "User"

    model_ref = "get_user_model()" if is_user else f'"{app_label}.{model_name}"'

    assignments: list[str] = []
    post_generations: list[str] = []
    get_or_create: list[str] = []

    for field in model_info["fields"]:
        rhs = _rhs_for(field, is_user)
        if rhs is None:
            continue
        if rhs == "many_to_many":
            post_generations.append(_m2m_method(field["name"]))
        elif field.get("unique") and not field.get("related"):
            assignments.append(f"    {field['name']} = {rhs}")
            get_or_create.append(field["name"])
        else:
            assignments.append(f"    {field['name']} = {rhs}")

    if is_user:
        get_or_create.append("username")

    body_lines = [
        "    class Meta:",
        f"        model = {model_ref}",
    ]
    if get_or_create:
        get_or_create = list(dict.fromkeys(get_or_create))
        rendered = ", ".join(_s(name) for name in get_or_create)
        if len(get_or_create) == 1:
            rendered = f"{rendered},"
        body_lines.append(f"        django_get_or_create = ({rendered})")
    body_lines.append("")
    body_lines.extend(assignments)
    if is_user:
        body_lines.append("")
        body_lines.append(_superuser_method())
    else:
        for method in post_generations:
            body_lines.append("")
            body_lines.append(method)

    class_body = "\n".join([f"class {class_name}(DjangoModelFactory):", *body_lines])
    return {
        "class_name": class_name,
        "class_body": class_body,
        "imports": [USER_IMPORT] if is_user else [],
    }


def _existing_class_names(source: str) -> set[str]:
    """Return the top-level class names declared in an existing module."""
    try:
        tree = ast.parse(source)
    except SyntaxError:  # pragma: no cover - file may be partially written
        return set()
    return {node.name for node in tree.body if isinstance(node, ast.ClassDef)}


def _insert_missing_imports(source: str, imports: list[str]) -> str:
    """Insert any ``imports`` not already present, after docstring/shebang."""
    missing = [line for line in imports if line not in source]
    if not missing:
        return source

    lines = source.splitlines()
    insert_at = 0
    while insert_at < len(lines):
        line = lines[insert_at]
        if line.startswith("#!") or not line.strip():
            insert_at += 1
            continue
        stripped = line.strip()
        if stripped.startswith(('"""', "'''")):
            quote = '"""' if '"""' in stripped else "'''"
            insert_at += 1
            if stripped.count(quote) < 2:  # multi-line docstring
                while insert_at < len(lines) and quote not in lines[insert_at]:
                    insert_at += 1
                insert_at += 1
        break
    while insert_at < len(lines) and lines[insert_at].startswith(("from ", "import ")):
        insert_at += 1

    lines[insert_at:insert_at] = missing
    return "\n".join(lines).rstrip("\n") + "\n"


def assemble_module(
    model_infos: list[dict], existing: str | None = None
) -> tuple[str, list[str], list[str]]:
    """Build the content of an app's ``factories.py`` module.

    When *existing* is None a fresh module (imports + factories) is built;
    otherwise new factory classes (and any missing imports) are merged into
    the existing source. Returns ``(content, added, skipped)`` where
    ``added``/``skipped`` are the class names created or left untouched.
    """
    factories = [build_factory(model_info) for model_info in model_infos]

    if existing is None:
        ordered = list(BASE_IMPORTS)
        for factory_ in factories:
            for line in factory_["imports"]:
                if line not in ordered:
                    ordered.append(line)
        header = "\n".join(ordered)
        blocks = "\n\n\n".join(factory_["class_body"] for factory_ in factories)
        return f"{header}\n\n\n{blocks}\n", [f["class_name"] for f in factories], []

    existing_names = _existing_class_names(existing)
    added: list[str] = []
    skipped: list[str] = []
    to_add = []
    for factory_ in factories:
        if factory_["class_name"] in existing_names:
            skipped.append(factory_["class_name"])
        else:
            added.append(factory_["class_name"])
            to_add.append(factory_)

    if not to_add:
        return existing, added, skipped

    source = _insert_missing_imports(existing, list(BASE_IMPORTS))
    extra_imports = [
        line
        for factory_ in to_add
        for line in factory_["imports"]
        if line not in source
    ]
    if extra_imports:
        source = _insert_missing_imports(source, extra_imports)

    for factory_ in to_add:
        source = source.rstrip("\n") + "\n\n\n" + factory_["class_body"] + "\n"
    return source, added, skipped


def module_path(project_root: Path, app_label: str) -> Path:
    """Return the ``<app_label>/factories.py`` path for an app."""
    return project_root / app_label / "factories.py"
