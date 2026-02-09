import typer
import requests

from pathlib import Path

from .....utils.django.project_manager import DjangoProjectManager
from .....utils.print_console import console


app = typer.Typer(no_args_is_help=True)
STARTING_POINT_UI_CSS_FILE_NAME = "starting-point-ui.min.css"
STARTING_POINT_UI_JS_FILE_NAME = "starting-point-ui.min.js"


def get_starting_point_ui_css_path() -> Path:
    """Get the path to the Starting Point UI CSS file."""
    pm = DjangoProjectManager()
    return pm.css_path / STARTING_POINT_UI_CSS_FILE_NAME


def get_starting_point_ui_js_path() -> Path:
    """Get the path to the Starting Point UI JS file."""
    pm = DjangoProjectManager()
    return pm.js_path / STARTING_POINT_UI_JS_FILE_NAME


@app.command()
def install():
    """
    Add Starting Point UI CSS framework to the project.

    Downloads the specified version (or latest) of Starting Point UI's minified CSS
    and JavaScript files, then saves them to the static directory.

    Starting Point UI is a Tailwind CSS v4+ component library.
    """

    pm = DjangoProjectManager()  # Validates Django project

    if not pm.has_dependency("django-tailwind-cli"):
        console.error(
            "django-tailwind-cli package is not set up in this project. Please install it by running:\n"
        )
        console.info("ddx backend django packages django-tailwind-cli install")
        raise typer.Exit(code=1)

    version = get_latest_version()
    download_starting_point_ui(version)
    add_import_to_input_css()
    add_links_to_base_template()

    console.success(
        f"Starting Point UI {version} with all dependencies successfully installed!"
    )


@app.command()
def remove():
    """
    Remove Starting Point UI CSS framework from the project.
    """
    pm = DjangoProjectManager()
    tailwind_css_dir = pm.project_path / "tailwind" / "src" / "css"
    starting_point_ui_css_file = tailwind_css_dir / STARTING_POINT_UI_CSS_FILE_NAME

    starting_point_ui_css_file.unlink(missing_ok=True)
    get_starting_point_ui_js_path().unlink(missing_ok=True)
    remove_import_from_input_css()
    remove_links_from_base_template()

    console.success("Starting Point UI removed successfully!")


def get_latest_version() -> str:
    api_url = "https://data.jsdelivr.com/v1/package/npm/starting-point-ui"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        version = response.json()["tags"]["latest"]
        console.info(f"Latest Starting Point UI version found: {version}")
        return version
    except Exception as e:
        console.error(f"An error occurred finding the latest version: {e}")
        raise typer.Exit(code=1)


def download_starting_point_ui(version: str) -> None:
    pm = DjangoProjectManager()

    # CSS goes to Tailwind source directory
    tailwind_css_dir = pm.project_path / "tailwind" / "src" / "css"
    starting_point_ui_css_file = tailwind_css_dir / STARTING_POINT_UI_CSS_FILE_NAME

    # JS goes to static directory
    starting_point_ui_js_file = get_starting_point_ui_js_path()
    js_path = pm.js_path

    files_to_download: list[dict[str, str | Path]] = [
        {
            "url": f"https://cdn.jsdelivr.net/npm/starting-point-ui@{version}/dist/index.min.css",
            "output_path": starting_point_ui_css_file,
            "description": "Starting Point UI CSS",
        },
        {
            "url": f"https://cdn.jsdelivr.net/npm/starting-point-ui@{version}/dist/index.js",
            "output_path": starting_point_ui_js_file,
            "description": "Starting Point UI JS",
        },
    ]

    try:
        tailwind_css_dir.mkdir(parents=True, exist_ok=True)
        js_path.mkdir(parents=True, exist_ok=True)
        for file_info in files_to_download:
            console.step(f"Downloading {file_info['description']} ...")

            response = requests.get(str(file_info["url"]))
            response.raise_for_status()

            Path(file_info["output_path"]).write_text(response.text)
            console.success(
                f"{file_info['description']} saved to {file_info['output_path']}"
            )
    except Exception as e:
        console.error(f"Error downloading Starting Point UI: {e}")
        raise typer.Exit(code=1)


def add_links_to_base_template() -> None:
    pm = DjangoProjectManager()
    base_template_path = pm.base_template_path
    content = base_template_path.read_text()

    if (
        STARTING_POINT_UI_CSS_FILE_NAME in content
        and STARTING_POINT_UI_JS_FILE_NAME in content
    ):
        return

    starting_point_ui_css = f"""<link rel="stylesheet" href="{{% static 'css/{STARTING_POINT_UI_CSS_FILE_NAME}' %}}">"""
    starting_point_ui_js = f"""  <script src="{{% static 'js/{STARTING_POINT_UI_JS_FILE_NAME}' %}}" type="module"></script>"""

    marker = "{% block extra_head %}{% endblock %}"
    content = content.replace(marker, starting_point_ui_css + "\n    " + marker)

    # Place script before closing body
    body_marker = "</body>"
    if body_marker in content:
        content = content.replace(
            body_marker, starting_point_ui_js + "\n  " + body_marker
        )

    base_template_path.write_text(content)


def remove_links_from_base_template() -> None:
    pm = DjangoProjectManager()
    base_template_path = pm.base_template_path

    new_lines = []
    removed = False
    with base_template_path.open("r") as f:
        for line in f:
            if (
                STARTING_POINT_UI_CSS_FILE_NAME in line
                or STARTING_POINT_UI_JS_FILE_NAME in line
            ):
                removed = True
                continue
            new_lines.append(line)

    if removed:
        base_template_path.write_text("".join(new_lines))


def add_import_to_input_css() -> None:
    pm = DjangoProjectManager()
    input_css_path = pm.project_path / "tailwind" / "src" / "css" / "input.css"

    content = input_css_path.read_text()
    import_statement = f'@import "./{STARTING_POINT_UI_CSS_FILE_NAME}";'

    if import_statement in content:
        return

    # Add import after tailwindcss import
    tailwindcss_import = '@import "tailwindcss";'
    content = content.replace(
        tailwindcss_import,
        f"{tailwindcss_import}\n{import_statement}",
    )

    input_css_path.write_text(content)
    console.success(f"Added import to {input_css_path}")


def remove_import_from_input_css() -> None:
    pm = DjangoProjectManager()
    input_css_path = pm.project_path / "tailwind" / "src" / "css" / "input.css"

    if not input_css_path.exists():
        return

    content = input_css_path.read_text()
    import_statement = f'@import "./{STARTING_POINT_UI_CSS_FILE_NAME}";'

    if import_statement in content:
        content = content.replace(import_statement + "\n", "")
        content = content.replace(import_statement, "")
        input_css_path.write_text(content)
        console.success(f"Removed import from {input_css_path}")
