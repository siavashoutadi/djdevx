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
BOOTSTRAP_CSS_FILE_NAME = "bootstrap.min.css"
BOOTSTRAP_JS_FILE_NAME = "bootstrap.bundle.min.js"
CSS_PATH = get_css_path()
JS_PATH = get_js_path()
BOOTSTRAP_CSS_FILE = CSS_PATH / BOOTSTRAP_CSS_FILE_NAME
BOOTSTRAP_JS_FILE = JS_PATH / BOOTSTRAP_JS_FILE_NAME


@app.command()
def install():
    """
    Add Bootstrap CSS framework to the project.

    Downloads the specified version (or latest) of Bootstrap's minified CSS, theme CSS,
    JavaScript files, and jQuery, then saves them to the static directory.
    """

    is_project_exists_or_raise()
    version = get_latest_version()
    download_bootstrap(version)
    add_links_to_base_template()

    print_success(f"Bootstrap {version} with all dependencies successfully installed!")


@app.command()
def remove():
    """
    Remove Bootstrap CSS framework from the project.
    """
    BOOTSTRAP_CSS_FILE.unlink(missing_ok=True)
    BOOTSTRAP_JS_FILE.unlink(missing_ok=True)
    remove_links_from_base_template()

    print_success("Bootstrap removed successfully!")


def get_latest_version() -> str:
    api_url = "https://data.jsdelivr.com/v1/package/npm/bootstrap"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        version = response.json()["tags"]["latest"]
        print_info(f"Latest Bootstrap version found: {version}")
        return version
    except Exception as e:
        print_error(f"An error occurred finding the latest version: {e}")
        raise typer.Exit(code=1)


def download_bootstrap(version: str) -> None:
    files_to_download: list[dict[str, str | Path]] = [
        {
            "url": f"https://cdn.jsdelivr.net/npm/bootstrap@{version}/dist/css/{BOOTSTRAP_CSS_FILE_NAME}",
            "output_path": BOOTSTRAP_CSS_FILE,
            "description": "Bootstrap CSS",
        },
        {
            "url": f"https://cdn.jsdelivr.net/npm/bootstrap@{version}/dist/js/{BOOTSTRAP_JS_FILE_NAME}",
            "output_path": BOOTSTRAP_JS_FILE,
            "description": "Bootstrap JS",
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
        print_error(f"Error downloading Bootstrap: {e}")
        raise typer.Exit(code=1)


def add_links_to_base_template() -> None:
    base_template_path = get_base_template_path()
    content = base_template_path.read_text()

    if BOOTSTRAP_CSS_FILE_NAME in content and BOOTSTRAP_JS_FILE_NAME in content:
        return

    bootstrap_css = f"""<link rel="stylesheet" href="{{% static 'css/{BOOTSTRAP_CSS_FILE_NAME}' %}}">"""

    bootstrap_js = (
        f"""  <script src="{{% static 'js/{BOOTSTRAP_JS_FILE_NAME}' %}}"></script>"""
    )

    css_marker = "{% block extra_head %}{% endblock %}"
    if css_marker in content:
        content = content.replace(css_marker, bootstrap_css + "\n    " + css_marker)

    js_marker = "</body>"
    if js_marker in content:
        content = content.replace(js_marker, bootstrap_js + "\n  " + js_marker)

    base_template_path.write_text(content)


def remove_links_from_base_template() -> None:
    base_template_path = get_base_template_path()

    new_lines = []
    removed = False
    with base_template_path.open("r") as f:
        for line in f:
            if BOOTSTRAP_CSS_FILE_NAME in line or BOOTSTRAP_JS_FILE_NAME in line:
                removed = True
                continue
            new_lines.append(line)

    if removed:
        base_template_path.write_text("".join(new_lines))
