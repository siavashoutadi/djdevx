import typer
import requests

from pathlib import Path

from ...utils.project_files import (
    get_base_template_path,
    is_project_exists_or_raise,
    get_css_path,
    get_js_path,
)
from ...utils.print_console import (
    print_info,
    print_step,
    print_success,
    print_error,
)


app = typer.Typer(no_args_is_help=True)
FRANKENUI_CSS_FILE_NAME = "frankenui-core.min.css"
FRANKENUI_CORE_JS_FILE_NAME = "frankenui-core.iife.js"
FRANKENUI_ICON_JS_FILE_NAME = "frankenui-icon.iife.js"
CSS_PATH = get_css_path()
JS_PATH = get_js_path()
FRANKENUI_CSS_FILE = CSS_PATH / FRANKENUI_CSS_FILE_NAME
FRANKENUI_CORE_JS_FILE = JS_PATH / FRANKENUI_CORE_JS_FILE_NAME
FRANKENUI_ICON_JS_FILE = JS_PATH / FRANKENUI_ICON_JS_FILE_NAME


@app.command()
def install():
    """
    Add FrankenUI CSS framework to the project.

    Downloads the specified version (or latest) of FrankenUI's minified CSS
    and JavaScript files, then saves them to the static directory.
    """

    is_project_exists_or_raise()
    version = get_latest_version()
    download_frankenui(version)
    add_links_to_base_template()

    print_success(f"FrankenUI {version} with all dependencies successfully installed!")


@app.command()
def remove():
    """
    Remove FrankenUI CSS framework from the project.
    """
    FRANKENUI_CSS_FILE.unlink(missing_ok=True)
    FRANKENUI_CORE_JS_FILE.unlink(missing_ok=True)
    FRANKENUI_ICON_JS_FILE.unlink(missing_ok=True)
    remove_links_from_base_template()

    print_success("FrankenUI removed successfully!")


def get_latest_version() -> str:
    api_url = "https://data.jsdelivr.com/v1/package/npm/franken-ui"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        version = response.json()["tags"]["latest"]
        print_info(f"Latest FrankenUI version found: {version}")
        return version
    except Exception as e:
        print_error(f"An error occurred finding the latest version: {e}")
        raise typer.Exit(code=1)


def download_frankenui(version: str) -> None:
    files_to_download: list[dict[str, str | Path]] = [
        {
            "url": f"https://cdn.jsdelivr.net/npm/franken-ui@{version}/dist/css/core.min.css",
            "output_path": FRANKENUI_CSS_FILE,
            "description": "FrankenUI CSS",
        },
        {
            "url": f"https://cdn.jsdelivr.net/npm/franken-ui@{version}/dist/js/core.iife.js",
            "output_path": FRANKENUI_CORE_JS_FILE,
            "description": "FrankenUI Core JS",
        },
        {
            "url": f"https://cdn.jsdelivr.net/npm/franken-ui@{version}/dist/js/icon.iife.js",
            "output_path": FRANKENUI_ICON_JS_FILE,
            "description": "FrankenUI Icon JS",
        },
    ]

    try:
        CSS_PATH.mkdir(parents=True, exist_ok=True)
        JS_PATH.mkdir(parents=True, exist_ok=True)
        for file_info in files_to_download:
            print_step(f"Downloading {file_info['description']} ...")

            response = requests.get(file_info["url"])
            response.raise_for_status()

            Path(file_info["output_path"]).write_text(response.text)
            print_success(
                f"{file_info['description']} saved to {file_info['output_path']}"
            )
    except Exception as e:
        print_error(f"Error downloading FrankenUI: {e}")
        raise typer.Exit(code=1)


def add_links_to_base_template() -> None:
    base_template_path = get_base_template_path()
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
    base_template_path = get_base_template_path()

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
