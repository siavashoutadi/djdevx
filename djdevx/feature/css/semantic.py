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
SEMANTIC_CSS_FILE_NAME = "semantic.min.css"
SEMANTIC_JS_FILE_NAME = "semantic.min.js"
JQUERY_FILE_NAME = "jquery-3.1.1.min.js"
CSS_PATH = get_css_path()
JS_PATH = get_js_path()
SEMANTIC_CSS_FILE = CSS_PATH / SEMANTIC_CSS_FILE_NAME
SEMANTIC_JS_FILE = JS_PATH / SEMANTIC_JS_FILE_NAME
JQUERY_FILE = JS_PATH / JQUERY_FILE_NAME


@app.command()
def install():
    """
    Add Semantic UI CSS framework to the project.

    Downloads the latest Semantic UI (from jsdelivr tags) and jQuery, saves them to the
    static directory, and updates the base template to include links.
    """

    is_project_exists_or_raise()
    version = get_latest_version()
    download_semantic(version)
    add_links_to_base_template()

    print_success(f"Semantic UI {version} with jQuery successfully installed!")


@app.command()
def remove():
    """
    Remove Semantic css framework from the project.
    """
    SEMANTIC_CSS_FILE.unlink(missing_ok=True)
    SEMANTIC_JS_FILE.unlink(missing_ok=True)
    JQUERY_FILE.unlink(missing_ok=True)
    remove_links_from_base_template()

    print_success("Semantic UI removed successfully!")


def get_latest_version() -> str:
    api_url = "https://data.jsdelivr.com/v1/package/npm/semantic-ui"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        # jsdelivr exposes tags.latest for many packages; if not present, fallback to version
        data = response.json()
        version = data.get("tags", {}).get("latest") or data.get("version")
        print_info(f"Latest Semantic UI version found: {version}")
        return version
    except Exception as e:
        print_error(f"An error occurred finding the latest version: {e}")
        raise typer.Exit(code=1)


def download_semantic(version: str) -> None:
    # Use jsdelivr CDN paths
    files_to_download: list[dict[str, str | Path]] = [
        {
            "url": f"https://cdn.jsdelivr.net/npm/semantic-ui@{version}/dist/semantic.min.css",
            "output_path": SEMANTIC_CSS_FILE,
            "description": "Semantic UI CSS",
        },
        {
            "url": f"https://cdn.jsdelivr.net/npm/semantic-ui@{version}/dist/semantic.min.js",
            "output_path": SEMANTIC_JS_FILE,
            "description": "Semantic UI JS",
        },
        {
            # jQuery required by Semantic UI 2.x
            "url": "https://code.jquery.com/jquery-3.1.1.min.js",
            "output_path": JQUERY_FILE,
            "description": "jQuery 3.1.1",
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
        print_error(f"Error downloading Semantic UI: {e}")
        raise typer.Exit(code=1)


def add_links_to_base_template() -> None:
    base_template_path = get_base_template_path()
    content = base_template_path.read_text()

    if (
        SEMANTIC_CSS_FILE_NAME in content
        and SEMANTIC_JS_FILE_NAME in content
        and JQUERY_FILE_NAME in content
    ):
        return

    semantic_css = f"""<link rel="stylesheet" href="{{% static 'css/{SEMANTIC_CSS_FILE_NAME}' %}}">"""
    jquery_js = f"""  <script src="{{% static 'js/{JQUERY_FILE_NAME}' %}}"></script>"""
    semantic_js = (
        f"""<script src="{{% static 'js/{SEMANTIC_JS_FILE_NAME}' %}}"></script>"""
    )

    marker = "{% block extra_head %}{% endblock %}"
    content = content.replace(marker, semantic_css + "\n    " + marker)

    # Place scripts before closing body
    body_marker = "</body>"
    if body_marker in content:
        content = content.replace(
            body_marker, jquery_js + "\n    " + semantic_js + "\n  " + body_marker
        )

    base_template_path.write_text(content)


def remove_links_from_base_template() -> None:
    base_template_path = get_base_template_path()

    new_lines = []
    removed = False
    with base_template_path.open("r") as f:
        for line in f:
            if (
                SEMANTIC_CSS_FILE_NAME in line
                or SEMANTIC_JS_FILE_NAME in line
                or JQUERY_FILE_NAME in line
            ):
                removed = True
                continue
            new_lines.append(line)

    if removed:
        base_template_path.write_text("".join(new_lines))
