import shutil
import subprocess
import typer
import tempfile

from pathlib import Path
from typing import Annotated, Tuple

from ..utils.project_files import is_project_exists_or_raise, get_admin_path, get_models

from ..utils.print_console import (
    print_info,
    print_diff,
    print_success,
    print_step,
    print_warning,
)

app = typer.Typer(no_args_is_help=True)


def find_related_models(model, all_models):
    """Find models that have ForeignKey to this model."""
    related = []
    model_name = model["name"]

    for other_model in all_models:
        for field in other_model["fields"]:
            if field["is_relation"] and field["related_model"] == model_name:
                related.append(other_model["name"])

    return related


def generate_inline_class(model_name):
    """Generate inline admin class."""
    return f"""class {model_name}Inline(admin.TabularInline):
    model = {model_name}
    extra = 1"""


def generate_admin_class(model, all_models):
    """Generate admin class for a model."""
    model_name = model["name"]
    fields = model["fields"]

    # Determine list_display (exclude large text fields)
    list_display = ["id"]
    text_field_types = [
        "TextField",
        "RichTextUploadingField",
        "BinaryField",
        "JSONField",
    ]

    for field in fields:
        if field["type"] not in text_field_types:
            list_display.append(field["name"])
        if len(list_display) >= 7:
            break

    # Determine list_filter (date, boolean, FK fields)
    list_filter = []
    filter_field_types = [
        "DateField",
        "DateTimeField",
        "BooleanField",
        "ForeignKey",
        "OneToOneField",
    ]

    for field in fields:
        if field["type"] in filter_field_types:
            list_filter.append(field["name"])

    # Determine search_fields (char and text fields)
    search_fields = []
    search_field_types = [
        "CharField",
        "TextField",
        "EmailField",
        "URLField",
        "SlugField",
    ]

    for field in fields:
        if field["type"] in search_field_types:
            search_fields.append(field["name"])
            if len(search_fields) >= 3:
                break

    # Determine raw_id_fields (FK fields)
    raw_id_fields = []
    for field in fields:
        if field["is_relation"] and field["type"] in ["ForeignKey", "OneToOneField"]:
            raw_id_fields.append(field["name"])

    # Find related models for inlines
    related_models = find_related_models(model, all_models)

    # Build admin class
    lines = [
        f"@admin.register({model_name})",
        f"class {model_name}Admin(admin.ModelAdmin):",
    ]

    if related_models:
        inlines_str = ", ".join([f"{name}Inline" for name in related_models])
        lines.append(f"    inlines = [{inlines_str}]")

    if list_display:
        list_display_str = ", ".join([f'"{f}"' for f in list_display])
        lines.append(f"    list_display = [{list_display_str}]")

    if list_filter:
        list_filter_str = ", ".join([f'"{f}"' for f in list_filter])
        lines.append(f"    list_filter = [{list_filter_str}]")

    if search_fields:
        search_fields_str = ", ".join([f'"{f}"' for f in search_fields])
        lines.append(f"    search_fields = [{search_fields_str}]")

    if raw_id_fields:
        raw_id_fields_str = ", ".join([f'"{f}"' for f in raw_id_fields])
        lines.append(f"    raw_id_fields = [{raw_id_fields_str}]")

    return "\n".join(lines)


def generate_admin_file_content(app_name: str) -> Tuple[Path, str]:
    """Generate complete admin.py file."""
    models = get_models(app_name)

    model_names = [m["name"] for m in models]
    imports = [
        "from django.contrib import admin",
        f"from .models import {', '.join(model_names)}",
        "",
        "",
    ]

    inline_sections = []
    for model in models:
        related = find_related_models(model, models)
        for related_name in related:
            inline_sections.append(generate_inline_class(related_name))

    admin_sections = []
    for model in models:
        admin_sections.append(generate_admin_class(model, models))

    content_parts = imports
    if inline_sections:
        content_parts.append("\n\n".join(inline_sections))
        content_parts.append("\n\n")
    content_parts.append("\n\n".join(admin_sections))

    content = "\n".join(content_parts) + "\n"

    return format_with_ruff(content)


def format_with_ruff(content: str) -> Tuple[Path, str]:
    temp_dir = Path(tempfile.mkdtemp(prefix="djdevx_"))
    file_path = temp_dir / "admin.py"
    file_path.write_text(content)

    subprocess.run(["uv", "run", "ruff", "format", file_path], check=True)
    formatted = file_path.read_text()

    return (file_path, formatted)


def get_admin_file_content(application_name: str) -> Tuple[Path, str]:
    admin_file = get_admin_path(application_name)
    if not admin_file.exists():
        return (admin_file, "")

    content = admin_file.read_text()
    return (admin_file, content)


def handle_admin_file_content(application_name: str, new_content: str) -> bool:
    admin_file, content = get_admin_file_content(application_name)
    if not content:
        admin_file.write_text(new_content)
        return True

    print_info(f"admin.py already exists at {admin_file}")

    if content == new_content:
        print_warning("No changes detected in admin.py. Skipping file write.")
        return True

    print_diff(
        content,
        new_content,
        title_old="admin.py (current)",
        title_new="admin.py (new)",
    )

    overwrite = typer.confirm("Overwrite file with the new content?", default=False)
    if overwrite:
        print_step("Writing updated content to admin.py ...")
        admin_file.write_text(new_content, encoding="utf-8")
        print_success("admin.py file has been updated successfully.")
        return True

    delete = typer.confirm("Delete the temporary file?", default=True)

    return delete


def create_admin(
    application_name: Annotated[
        str,
        typer.Option(
            help="Application name",
            prompt="Please enter the application name",
        ),
    ] = "",
):
    """
    Create admin.py from application
    """
    print_step(f"Creating admin.py for {application_name} application ...")

    is_project_exists_or_raise()

    new_file, content = generate_admin_file_content(application_name)
    should_delete = True
    try:
        should_delete = handle_admin_file_content(application_name, content)
    finally:
        if should_delete:
            shutil.rmtree(new_file.parent, ignore_errors=True)
