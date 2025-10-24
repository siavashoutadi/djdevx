import subprocess
import typer
from pathlib import Path
from typing_extensions import Annotated

from ..utils.print_console import print_step, print_success
from ..utils.project_info import has_dependency
from ..utils.project_files import (
    copy_template_files,
    is_project_exists_or_raise,
    get_project_path,
    get_packages_settings_path,
    get_base_template_path,
)

app = typer.Typer(no_args_is_help=True)


def add_snakeoil_to_base_template() -> None:
    """Add {% load snakeoil %} and {% meta %} to base template"""
    base_template_path = get_base_template_path()
    content = base_template_path.read_text()

    if "{% load snakeoil %}" in content and "{% meta %}" in content:
        return

    if "{% load snakeoil %}" not in content:
        content = content.replace(
            "{% load static %}", "{% load static %}\n{% load snakeoil %}"
        )

    if "{% meta %}" not in content:
        # Place {% meta %} after the viewport meta tag
        viewport_marker = (
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
        )

        if viewport_marker in content:
            content = content.replace(
                viewport_marker, viewport_marker + "\n    {% meta %}"
            )

    base_template_path.write_text(content)


def remove_snakeoil_from_base_template() -> None:
    """Remove {% load snakeoil %} and {% meta %} from base template"""
    base_template_path = get_base_template_path()

    new_lines = []
    removed = False
    with base_template_path.open("r") as f:
        for line in f:
            if "{% load snakeoil %}" in line or "{% meta %}" in line:
                removed = True
                continue
            new_lines.append(line)

    if removed:
        base_template_path.write_text("".join(new_lines))


@app.command()
def install(
    site_name: Annotated[
        str,
        typer.Option(
            help="Display name of your website for og:site_name meta tag (e.g., 'My Blog')",
            prompt="Please enter your site name",
        ),
    ] = "",
    site_description: Annotated[
        str,
        typer.Option(
            help="Default description for your website (shown in search results and social shares)",
            prompt="Please enter your site description (leave empty to skip)",
        ),
    ] = "",
    author: Annotated[
        str,
        typer.Option(
            help="Default author name for meta author tag",
            prompt="Please enter default author name (leave empty to skip)",
        ),
    ] = "",
    og_type: Annotated[
        str,
        typer.Option(
            help="OpenGraph type for og:type meta tag (website, article, blog). See: https://ogp.me/#types",
            prompt="Please enter OpenGraph type (website/article/blog)",
        ),
    ] = "website",
    default_image_url: Annotated[
        str,
        typer.Option(
            help="Full URL to default share image for social media (1200x630px recommended), or leave as default to use images/logo.svg",
            prompt="Enter default image URL for social sharing (or press Enter for images/logo.svg)",
        ),
    ] = "images/logo.svg",
    site_url: Annotated[
        str,
        typer.Option(
            help="Your website's full URL including protocol (e.g., 'https://example.com')",
            prompt="Please enter your site URL (e.g., https://example.com, leave empty to skip)",
        ),
    ] = "",
    locale: Annotated[
        str,
        typer.Option(
            help="Default locale/language for og:locale (e.g., 'en_US', 'en_GB', 'es_ES')",
            prompt="Please enter your site locale (e.g., en_US, leave empty to skip)",
        ),
    ] = "",
    twitter_site: Annotated[
        str,
        typer.Option(
            help="Twitter/X handle for your website (e.g., '@yoursite')",
            prompt="Please enter your Twitter/X handle (e.g., @yoursite, leave empty to skip)",
        ),
    ] = "",
    twitter_card_type: Annotated[
        str,
        typer.Option(
            help="Twitter card type: 'summary' or 'summary_large_image' (recommended for rich previews)",
            prompt="Please enter Twitter card type (summary/summary_large_image)",
        ),
    ] = "summary_large_image",
    keywords: Annotated[
        str,
        typer.Option(
            help="Default keywords for SEO (comma-separated, e.g., 'django, web development, python')",
            prompt="Please enter default keywords (comma-separated, leave empty to skip)",
        ),
    ] = "",
):
    """
    Install and configure django-snakeoil for SEO metadata management
    """
    is_project_exists_or_raise()

    print_step("Installing django-snakeoil package ...")

    subprocess.check_call(["uv", "add", "django-snakeoil"])

    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir.parent / "templates" / "django-snakeoil"
    project_dir = get_project_path()

    template_context = {
        "site_name": site_name,
        "site_description": site_description,
        "author": author,
        "og_type": og_type,
        "default_image_url": default_image_url,
        "site_url": site_url,
        "locale": locale,
        "twitter_site": twitter_site,
        "twitter_card_type": twitter_card_type,
        "keywords": keywords,
    }

    copy_template_files(
        source_dir=source_dir,
        dest_dir=project_dir,
        template_context=template_context,
    )

    add_snakeoil_to_base_template()

    print_success("django-snakeoil is installed successfully.")


@app.command()
def remove():
    """
    Remove django-snakeoil
    """
    print_step("Removing django-snakeoil package ...")

    if has_dependency("django-snakeoil"):
        subprocess.check_call(["uv", "remove", "django-snakeoil"])

    settings_path = Path.joinpath(get_packages_settings_path(), "django_snakeoil.py")
    settings_path.unlink(missing_ok=True)

    remove_snakeoil_from_base_template()

    print_success("django-snakeoil is removed successfully.")
