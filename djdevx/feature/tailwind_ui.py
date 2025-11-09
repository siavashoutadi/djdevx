import typer
import shutil

from pathlib import Path

from ..utils.project_info import has_dependency

from ..utils.project_files import (
    copy_template_files,
    is_project_exists_or_raise,
    get_project_path,
)

from ..utils.print_console import print_success, print_error
from ..utils.file_content_change import remove_lines_from_file

app = typer.Typer(no_args_is_help=True)


@app.command()
def install():
    """Install Tailwind UI"""

    is_project_exists_or_raise()

    if not has_dependency("heroicons"):
        print_error(
            "Heroicons is not installed. Please install it first by running: ddx packages heroicons install"
        )
        raise typer.Exit(code=1)

    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir.parent / "templates" / "tailwind-ui"
    project_path = get_project_path()

    theme_css_path = project_path / "tailwind" / "src" / "css" / "theme.css"

    if not theme_css_path.exists():
        print_error(
            "Tailwind theme is not installed. Please install Tailwind theme first.\nInstall it by running: djdevx feature tailwind-theme install"
        )
        raise typer.Exit(code=1)

    input_css_path = project_path / "tailwind" / "src" / "css" / "input.css"

    copy_template_files(source_dir, project_path, {})

    input_content = input_css_path.read_text(encoding="utf-8")

    import_tailwind = '@import "tailwindcss";'
    ui_import = '@import "./tailwind-ui/all.css";'

    if import_tailwind in input_content:
        replace_with = f"{import_tailwind}"
        if ui_import not in input_content:
            replace_with = f"{replace_with}\n{ui_import}"

        input_content = input_content.replace(import_tailwind, replace_with)

    input_css_path.write_text(input_content, encoding="utf-8")

    print_success("Tailwind UI installed successfully.")


@app.command()
def remove():
    """Remove Tailwind UI."""

    is_project_exists_or_raise()

    project_path = get_project_path()

    tailwind_ui_app_path = project_path / "tailwind_ui"
    tailwind_css_ui_path = project_path / "tailwind" / "src" / "css" / "tailwind-ui"
    input_css_path = project_path / "tailwind" / "src" / "css" / "input.css"
    tailwind_url_path = project_path / "urls" / "apps" / "tailwind_ui.py"
    tailwind_settings_path = project_path / "settings" / "apps" / "tailwind_ui.py"

    shutil.rmtree(tailwind_ui_app_path, ignore_errors=True)
    shutil.rmtree(tailwind_css_ui_path, ignore_errors=True)
    tailwind_url_path.unlink(missing_ok=True)
    tailwind_settings_path.unlink(missing_ok=True)

    if input_css_path.exists():
        remove_lines_from_file(
            input_css_path,
            ["tailwind-ui"],
        )

    print_success("Tailwind UI removed successfully.")
