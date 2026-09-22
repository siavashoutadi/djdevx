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


def _render_get_or_create(names: list[str]) -> str:
    """Render the ``Meta.django_get_or_create`` tuple from ordered names."""
    rendered = ", ".join(_s(name) for name in names)
    if len(names) == 1:
        rendered = f"{rendered},"
    return f"({rendered})"


def build_factory(model_info: dict) -> dict:
    """Build the source body for one factory class.

    Returns a dict with ``class_name``, ``class_body`` (the full indented
    class definition, without trailing newline), ``imports`` (extra module
    imports the class needs) plus the structured declarations required for
    additive merges: ``fields`` (``name -> RHS``), ``m2m`` (``name -> method
    source``) and ``get_or_create`` (ordered unique-attribute names).
    """
    app_label = model_info["app_label"]
    model_name = model_info["name"]
    class_name = f"{model_name}Factory"
    is_user = model_name == "User"

    model_ref = "get_user_model()" if is_user else f'"{app_label}.{model_name}"'

    assignments: list[str] = []
    post_generations: list[str] = []
    fields: dict[str, str] = {}
    m2m: dict[str, str] = {}
    get_or_create: list[str] = []

    for field in model_info["fields"]:
        rhs = _rhs_for(field, is_user)
        if rhs is None:
            continue
        if rhs == "many_to_many":
            method = _m2m_method(field["name"])
            post_generations.append(method)
            m2m[field["name"]] = method
            continue
        if field.get("unique") and not field.get("related"):
            get_or_create.append(field["name"])
        assignments.append(f"    {field['name']} = {rhs}")
        fields[field["name"]] = rhs

    if is_user:
        get_or_create.append("username")

    body_lines = [
        "    class Meta:",
        f"        model = {model_ref}",
    ]
    if get_or_create:
        get_or_create = list(dict.fromkeys(get_or_create))
        body_lines.append(
            f"        django_get_or_create = {_render_get_or_create(get_or_create)}"
        )
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
        "fields": fields,
        "m2m": m2m,
        "get_or_create": get_or_create,
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


def _class_declared_names(node: ast.ClassDef) -> set[str]:
    """Return names of top-level assignments and methods declared in a class."""
    declared: set[str] = set()
    for stmt in node.body:
        if isinstance(stmt, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            declared.add(stmt.name)
        elif isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name):
                    declared.add(target.id)
        elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            declared.add(stmt.target.id)
    return declared


def _meta_get_or_create(
    meta: ast.ClassDef, base: int
) -> tuple[int, list[str] | None] | None:
    """Locate the ``Meta.django_get_or_create`` assignment of a factory class.

    Returns ``(slice-relative index, ordered names)`` for a parseable
    tuple/list assignment, ``(index, None)`` when the value is dynamic, or
    None when there is no such assignment. *base* is the class's first line
    number (1-based) used to compute the index within the class slice.
    """
    for stmt in meta.body:
        if not (
            isinstance(stmt, ast.Assign)
            and isinstance(stmt.targets[0], ast.Name)
            and stmt.targets[0].id == "django_get_or_create"
        ):
            continue
        try:
            value = ast.literal_eval(stmt.value)
        except ValueError, TypeError:
            return stmt.lineno - base, None
        names = value if isinstance(value, (tuple, list)) else [value]
        return stmt.lineno - base, [str(name) for name in names]
    return None


def _merge_class_source(source: str, node: ast.ClassDef, factory_: dict) -> str | None:
    """Merge declarations missing from an existing factory class.

    Appends any model fields, many-to-many post-generation hooks and
    ``django_get_or_create`` names not yet present, preserving existing lines
    (including manual edits). Returns the updated module source, or None when
    the class is already complete or cannot be merged safely.
    """
    declared = _class_declared_names(node)
    meta = next(
        (
            stmt
            for stmt in node.body
            if isinstance(stmt, ast.ClassDef) and stmt.name == "Meta"
        ),
        None,
    )
    if meta is None:
        return None

    missing_fields = [
        (name, rhs) for name, rhs in factory_["fields"].items() if name not in declared
    ]
    missing_m2m = [name for name in factory_["m2m"] if name not in declared]

    base = node.lineno
    goc = _meta_get_or_create(meta, base)
    if goc is None:
        missing_unique = list(factory_["get_or_create"])
    else:
        index, names = goc
        if names is None:
            missing_unique = []  # dynamic value: leave it untouched
        else:
            missing_unique = [n for n in factory_["get_or_create"] if n not in names]

    if not missing_fields and not missing_m2m and not missing_unique:
        return None

    lines = source.splitlines()
    class_start = base - 1
    class_end = node.end_lineno
    slice_ = lines[class_start:class_end]
    meta_end = meta.end_lineno - base

    if missing_fields:
        insert_at = meta_end + 1
        while insert_at < len(slice_) and not slice_[insert_at].strip():
            insert_at += 1
        new_lines = [f"    {name} = {rhs}" for name, rhs in missing_fields]
        if insert_at == meta_end + 1:
            new_lines = ["", *new_lines]
        slice_[insert_at:insert_at] = new_lines

    if missing_unique:
        if goc is None:
            model_idx = next(
                (
                    i
                    for i, stmt in enumerate(meta.body)
                    if isinstance(stmt, ast.Assign)
                    and isinstance(stmt.targets[0], ast.Name)
                    and stmt.targets[0].id == "model"
                ),
                None,
            )
            if model_idx is None:
                return None
            model_line = meta.body[model_idx].lineno
            insert_at = model_line - base + 1
            slice_[insert_at:insert_at] = [
                f"        django_get_or_create = {_render_get_or_create(missing_unique)}"
            ]
        else:
            index, names = goc
            line = slice_[index]
            indent = line[: len(line) - len(line.lstrip())]
            slice_[index] = (
                f"{indent}django_get_or_create = "
                f"{_render_get_or_create([*names, *missing_unique])}"
            )

    if missing_m2m:
        while slice_ and not slice_[-1].strip():
            slice_.pop()
        for name in missing_m2m:
            slice_.extend(["", factory_["m2m"][name]])

    if slice_ == lines[class_start:class_end]:
        return None
    lines[class_start:class_end] = slice_
    return "\n".join(lines).rstrip("\n") + "\n"


def _merge_factory(source: str, class_name: str, factory_: dict) -> str | None:
    """Merge declarations missing from the existing factory *class_name*."""
    try:
        tree = ast.parse(source)
    except SyntaxError:  # pragma: no cover - file may be partially written
        return None
    node = next(
        (
            stmt
            for stmt in tree.body
            if isinstance(stmt, ast.ClassDef) and stmt.name == class_name
        ),
        None,
    )
    if node is None:
        return None
    return _merge_class_source(source, node, factory_)


def assemble_module(
    model_infos: list[dict], existing: str | None = None
) -> tuple[str, list[str], list[str], list[str]]:
    """Build the content of an app's ``factories.py`` module.

    When *existing* is None a fresh module (imports + factories) is built;
    otherwise new factory classes are appended and existing classes are
    refreshed in place with any declarations the model gained since the last
    run (new fields, many-to-many hooks, unique attributes). Returns
    ``(content, added, skipped, updated)`` where ``added``/``skipped`` are the
    class names created or left untouched and ``updated`` the existing classes
    that gained declarations.
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
        content = f"{header}\n\n\n{blocks}\n"
        return content, [f["class_name"] for f in factories], [], []

    existing_names = _existing_class_names(existing)
    added: list[str] = []
    skipped: list[str] = []
    updated: list[str] = []
    to_add = []
    for factory_ in factories:
        name = factory_["class_name"]
        if name not in existing_names:
            added.append(name)
            to_add.append(factory_)
            continue
        merged = _merge_factory(existing, name, factory_)
        if merged is None:
            skipped.append(name)
        else:
            existing = merged
            updated.append(name)

    if not to_add:
        return existing, added, skipped, updated

    missing_imports = list(BASE_IMPORTS)
    for factory_ in to_add:
        for line in factory_["imports"]:
            if line not in missing_imports:
                missing_imports.append(line)
    source = _insert_missing_imports(existing, missing_imports)
    for factory_ in to_add:
        source = source.rstrip("\n") + "\n\n\n" + factory_["class_body"] + "\n"
    return source, added, skipped, updated


def module_path(project_root: Path, app_label: str) -> Path:
    """Return the ``<app_label>/factories.py`` path for an app."""
    return project_root / app_label / "factories.py"
