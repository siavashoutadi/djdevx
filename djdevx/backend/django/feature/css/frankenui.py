import typer
import requests

from pathlib import Path

from .....utils.django.project_manager import DjangoProjectManager
from .....utils.print_console import console


app = typer.Typer(no_args_is_help=True)
FRANKENUI_CSS_FILE_NAME = "frankenui-core.min.css"
FRANKENUI_CORE_JS_FILE_NAME = "frankenui-core.iife.js"
FRANKENUI_ICON_JS_FILE_NAME = "frankenui-icon.iife.js"


def get_frankenui_css_path() -> Path:
    """Get the path to the FrankenUI CSS file."""
    pm = DjangoProjectManager()
    return pm.css_path / FRANKENUI_CSS_FILE_NAME


def get_frankenui_core_js_path() -> Path:
    """Get the path to the FrankenUI core JS file."""
    pm = DjangoProjectManager()
    return pm.js_path / FRANKENUI_CORE_JS_FILE_NAME


def get_frankenui_icon_js_path() -> Path:
    """Get the path to the FrankenUI icon JS file."""
    pm = DjangoProjectManager()
    return pm.js_path / FRANKENUI_ICON_JS_FILE_NAME


@app.command()
def install():
    """
    Add FrankenUI CSS framework to the project.

    Downloads the specified version (or latest) of FrankenUI's minified CSS
    and JavaScript files, then saves them to the static directory.
    """

    DjangoProjectManager()  # Validates Django project
    version = get_latest_version()
    download_frankenui(version)
    add_links_to_base_template()

    console.success(
        f"FrankenUI {version} with all dependencies successfully installed!"
    )


@app.command()
def remove():
    """
    Remove FrankenUI CSS framework from the project.
    """
    get_frankenui_css_path().unlink(missing_ok=True)
    get_frankenui_core_js_path().unlink(missing_ok=True)
    get_frankenui_icon_js_path().unlink(missing_ok=True)
    remove_links_from_base_template()

    console.success("FrankenUI removed successfully!")


def get_latest_version() -> str:
    api_url = "https://data.jsdelivr.com/v1/package/npm/franken-ui"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        version = response.json()["tags"]["latest"]
        console.info(f"Latest FrankenUI version found: {version}")
        return version
    except Exception as e:
        console.error(f"An error occurred finding the latest version: {e}")
        raise typer.Exit(code=1)


def download_frankenui(version: str) -> None:
    frankenui_css_file = get_frankenui_css_path()
    frankenui_core_js_file = get_frankenui_core_js_path()
    frankenui_icon_js_file = get_frankenui_icon_js_path()
    pm = DjangoProjectManager()
    css_path = pm.css_path
    js_path = pm.js_path

    files_to_download: list[dict[str, str | Path]] = [
        {
            "url": f"https://cdn.jsdelivr.net/npm/franken-ui@{version}/dist/css/core.min.css",
            "output_path": frankenui_css_file,
            "description": "FrankenUI CSS",
        },
        {
            "url": f"https://cdn.jsdelivr.net/npm/franken-ui@{version}/dist/js/core.iife.js",
            "output_path": frankenui_core_js_file,
            "description": "FrankenUI Core JS",
        },
        {
            "url": f"https://cdn.jsdelivr.net/npm/franken-ui@{version}/dist/js/icon.iife.js",
            "output_path": frankenui_icon_js_file,
            "description": "FrankenUI Icon JS",
        },
    ]

    try:
        css_path.mkdir(parents=True, exist_ok=True)
        js_path.mkdir(parents=True, exist_ok=True)
        for file_info in files_to_download:
            console.step(f"Downloading {file_info['description']} ...")

            response = requests.get(file_info["url"])
            response.raise_for_status()

            Path(file_info["output_path"]).write_text(response.text)
            console.success(
                f"{file_info['description']} saved to {file_info['output_path']}"
            )
    except Exception as e:
        console.error(f"Error downloading FrankenUI: {e}")
        raise typer.Exit(code=1)


def add_links_to_base_template() -> None:
    pm = DjangoProjectManager()
    base_template_path = pm.base_template_path
    content = base_template_path.read_text()

    if (
        FRANKENUI_CSS_FILE_NAME in content
        and FRANKENUI_CORE_JS_FILE_NAME in content
        and FRANKENUI_ICON_JS_FILE_NAME in content
    ):
        return

    frankenui_css = f"""<link rel="stylesheet" href="{{% static 'css/{FRANKENUI_CSS_FILE_NAME}' %}}">"""
    frankenui_core_js = f"""<script src="{{% static 'js/{FRANKENUI_CORE_JS_FILE_NAME}' %}}" type="module"></script>"""
    frankenui_icon_js = f"""<script src="{{% static 'js/{FRANKENUI_ICON_JS_FILE_NAME}' %}}" type="module"></script>"""

    marker = "{% block extra_head %}{% endblock %}"
    content = content.replace(marker, frankenui_css + "\n    " + marker)
    content = content.replace(marker, frankenui_core_js + "\n    " + marker)
    content = content.replace(marker, frankenui_icon_js + "\n    " + marker)

    base_template_path.write_text(content)


def remove_links_from_base_template() -> None:
    pm = DjangoProjectManager()
    base_template_path = pm.base_template_path

    new_lines = []
    removed = False
    with base_template_path.open("r") as f:
        for line in f:
            if (
                FRANKENUI_CSS_FILE_NAME in line
                or FRANKENUI_CORE_JS_FILE_NAME in line
                or FRANKENUI_ICON_JS_FILE_NAME in line
            ):
                removed = True
                continue
            new_lines.append(line)

    if removed:
        base_template_path.write_text("".join(new_lines))
