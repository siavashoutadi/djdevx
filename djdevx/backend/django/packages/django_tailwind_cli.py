import fileinput
import typer
from pathlib import Path

from ....utils.django.uv_runner import UvRunner
from ....utils.print_console import console
from ....utils.django.project_manager import DjangoProjectManager

app = typer.Typer(no_args_is_help=True)


def add_tailwind_snippets():
    pm = DjangoProjectManager()
    base_template = pm.base_template_path
    content = base_template.read_text()

    if "{% load tailwind_cli %}" not in content:
        content = "{% load tailwind_cli %}\n" + content

    if "{% tailwind_css %}" not in content:
        content = content.replace("</head>", "  {% tailwind_css %}\n  </head>")

    if '{% include "./_tw_dark_mode.html" %}' not in content:
        content = content.replace(
            "</head>", '  {% include "./_tw_dark_mode.html" %}\n  </head>'
        )

    base_template.write_text(content)


def remove_tailwind_snippets():
    pm = DjangoProjectManager()
    base_template = pm.base_template_path
    with fileinput.input(files=[base_template], inplace=True) as f:
        for line in f:
            if (
                "{% load tailwind_cli %}" not in line
                and "{% tailwind_css %}" not in line
                and '{% include "./_tw_dark_mode.html" %}' not in line
            ):
                print(line, end="")


def add_input_css_to_git_ignore():
    ignore_line = "/static/css/tailwind.min.css"

    pm = DjangoProjectManager()
    git_ignore = pm.gitignore_path
    content = git_ignore.read_text()

    if ignore_line not in content:
        content = content + ignore_line

    git_ignore.write_text(content)


def remove_input_css_to_git_ignore():
    pm = DjangoProjectManager()
    git_ignore = pm.gitignore_path
    with fileinput.input(files=[git_ignore], inplace=True) as f:
        for line in f:
            if "/static/css/tailwind.min.css" not in line:
                print(line, end="")


def add_tailwind_build_to_docker_file():
    console.step("Updating Dockerfile ...")
    build_static_line = "uv run manage.py collectstatic --noinput && \\"
    tailwind_build_line = "uv run manage.py tailwind build --force && \\"

    pm = DjangoProjectManager()
    docker_file = pm.dockerfile_path
    content = docker_file.read_text()

    if tailwind_build_line not in content:
        content = content.replace(
            build_static_line, tailwind_build_line + "\n    " + build_static_line
        )

    docker_file.write_text(content)


def remove_tailwind_build_to_docker_file():
    pm = DjangoProjectManager()
    docker_file = pm.dockerfile_path
    with fileinput.input(files=[docker_file], inplace=True) as f:
        for line in f:
            if "uv run manage.py tailwind build" not in line:
                print(line, end="")


@app.command()
def install():
    """
    Install and configure django-tailwind-cli
    """
    pm = DjangoProjectManager()

    console.step("Installing django-tailwind-cli package ...")
    uv_runner = UvRunner()
    uv_runner.add_package("django-tailwind-cli")

    current_dir = Path(__file__).resolve().parent
    source_dir = (
        current_dir.parent.parent.parent
        / "templates"
        / "django"
        / "django_tailwind_cli"
    )

    pm.copy_templates(source_dir=source_dir, template_context={})

    add_tailwind_snippets()
    add_input_css_to_git_ignore()
    add_tailwind_build_to_docker_file()

    console.success("django-tailwind-cli is installed successfully.")


@app.command()
def remove():
    """
    Remove django-tailwind-cli
    """
    console.step("Removing django-tailwind-cli package ...")

    pm = DjangoProjectManager()
    uv_runner = UvRunner()
    if pm.has_dependency("django-tailwind-cli"):
        uv_runner.remove_package("django-tailwind-cli")

    settings_url = Path.joinpath(pm.packages_settings_path, "django_tailwind_cli.py")
    settings_url.unlink(missing_ok=True)

    remove_tailwind_snippets()

    tailwind_conifg = Path.joinpath(pm.project_path, "tailwind.config.js")
    tailwind_conifg.unlink(missing_ok=True)

    tailwind_css_input = Path.joinpath(
        pm.project_path, "tailwind", "src", "css", "input.css"
    )
    tailwind_css_input.unlink(missing_ok=True)
    tailwind_css_output = Path.joinpath(
        pm.project_path, "static", "css", "tailwind.min.css"
    )
    tailwind_css_output.unlink(missing_ok=True)

    tailwind_dark_mode = Path.joinpath(
        pm.project_path, "templates", "_tw_dark_mode.html"
    )
    tailwind_dark_mode.unlink(missing_ok=True)

    remove_input_css_to_git_ignore()
    remove_tailwind_build_to_docker_file()

    console.success("django-tailwind-cli is removed successfully.")
