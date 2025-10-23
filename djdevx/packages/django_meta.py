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
)

app = typer.Typer(no_args_is_help=True)


@app.command()
def install(
    site_protocol: Annotated[
        str,
        typer.Option(
            help="Protocol for your site URL: 'http' or 'https' (use https for production)",
            prompt="Please enter your site protocol (http/https)",
        ),
    ] = "https",
    site_domain: Annotated[
        str,
        typer.Option(
            help="Your website domain without protocol (e.g., 'example.com' or 'blog.example.com')",
            prompt="Please enter your site domain (e.g., example.com)",
        ),
    ] = "",
    site_name: Annotated[
        str,
        typer.Option(
            help="Display name of your website (e.g., 'My Awesome Blog')",
            prompt="Please enter your site name",
        ),
    ] = "",
    site_type: Annotated[
        str,
        typer.Option(
            help="OpenGraph type (website, article, blog, product). See: https://ogp.me/#types",
            prompt="Please enter your site type (website/article/blog/product)",
        ),
    ] = "website",
    use_og_properties: Annotated[
        bool,
        typer.Option(
            help="Enable OpenGraph meta tags for rich previews on Facebook, LinkedIn, WhatsApp, etc.",
            prompt="Enable OpenGraph properties (Facebook, LinkedIn, WhatsApp)?",
        ),
    ] = True,
    use_twitter_properties: Annotated[
        bool,
        typer.Option(
            help="Enable Twitter Card meta tags for rich previews when links are shared on Twitter/X",
            prompt="Enable Twitter Card properties for rich previews on Twitter/X?",
        ),
    ] = True,
    use_schemaorg_properties: Annotated[
        bool,
        typer.Option(
            help="Enable Schema.org structured data for better SEO and search engine understanding",
            prompt="Enable Schema.org properties for better SEO?",
        ),
    ] = True,
    use_title_tag: Annotated[
        bool,
        typer.Option(
            help="Auto-render <title> tags in templates (disable if you manage titles manually)",
            prompt="Render <title> tag automatically?",
        ),
    ] = True,
    configure_facebook: Annotated[
        bool,
        typer.Option(
            help="Configure Facebook-specific settings (App ID, Pages, Publisher). Info: https://developers.facebook.com/docs/sharing/webmasters",
            prompt="Do you want to configure Facebook/OpenGraph settings?",
        ),
    ] = False,
    fb_app_id: Annotated[
        str,
        typer.Option(
            help="Facebook App ID from https://developers.facebook.com/apps/ (numeric ID, e.g., '123456789012345')",
        ),
    ] = "",
    fb_pages: Annotated[
        str,
        typer.Option(
            help="Facebook Page ID for your business page (numeric ID, find at facebook.com/your-page/about)",
        ),
    ] = "",
    fb_publisher: Annotated[
        str,
        typer.Option(
            help="Full Facebook Page URL (e.g., 'https://www.facebook.com/YourPageName')",
        ),
    ] = "",
    configure_twitter: Annotated[
        bool,
        typer.Option(
            help="Configure Twitter Card settings for rich previews. Guide: https://developer.twitter.com/en/docs/twitter-for-websites/cards/overview/abouts-cards",
            prompt="Do you want to configure Twitter Card settings?",
        ),
    ] = False,
    twitter_site: Annotated[
        str,
        typer.Option(
            help="Your website's Twitter/X handle including @ (e.g., '@YourSite')",
        ),
    ] = "",
    twitter_author: Annotated[
        str,
        typer.Option(
            help="Default author Twitter/X handle with @ (e.g., '@AuthorName')",
        ),
    ] = "",
    twitter_type: Annotated[
        str,
        typer.Option(
            help="Twitter Card type: 'summary' (small image) or 'summary_large_image' (large image, recommended)",
        ),
    ] = "summary_large_image",
    default_image_url: Annotated[
        str,
        typer.Option(
            help="Full URL to default share image (1200x630px recommended, e.g., 'https://example.com/share.jpg')",
            prompt="Enter default image URL for social sharing (leave empty to skip)",
        ),
    ] = "",
):
    """
    Install and configure django-meta
    """
    is_project_exists_or_raise()

    # Prompt for Facebook details if user wants to configure
    if configure_facebook:
        if not fb_app_id:
            typer.echo("\nGet your App ID from: https://developers.facebook.com/apps/")
            fb_app_id = typer.prompt(
                "Enter your Facebook App ID (numeric, e.g., 123456789012345) or leave empty",
                default="",
            )
        if not fb_pages:
            typer.echo("\nFind your Page ID at: facebook.com/your-page/about")
            fb_pages = typer.prompt(
                "Enter your Facebook Page ID (numeric) or leave empty", default=""
            )
        if not fb_publisher:
            typer.echo("\nUse your full Facebook Page URL")
            fb_publisher = typer.prompt(
                "Enter your Facebook Page URL (e.g., https://www.facebook.com/YourPage) or leave empty",
                default="",
            )

    # Prompt for Twitter details if user wants to configure
    if configure_twitter:
        if not twitter_site:
            typer.echo("\nEnter your website's Twitter/X handle")
            twitter_site = typer.prompt("Your site's Twitter handle (e.g., @YourSite)")
        if not twitter_author:
            typer.echo("\nDefault author handle for content attribution")
            twitter_author = typer.prompt(
                "Default author Twitter handle (e.g., @AuthorName) or leave empty",
                default="",
            )
        if not twitter_type:
            typer.echo(
                "\nCard types: 'summary' (small image) or 'summary_large_image' (large image, recommended)"
            )
            twitter_type = typer.prompt(
                "Twitter card type", default="summary_large_image"
            )

    print_step("Installing django-meta package ...")
    subprocess.check_call(["uv", "add", "django-meta"])

    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir.parent / "templates" / "django-meta"
    project_dir = get_project_path()

    template_context = {
        "site_protocol": site_protocol,
        "site_domain": site_domain,
        "site_name": site_name,
        "site_type": site_type,
        "use_og_properties": use_og_properties,
        "use_twitter_properties": use_twitter_properties,
        "use_schemaorg_properties": use_schemaorg_properties,
        "use_title_tag": use_title_tag,
        "configure_facebook": configure_facebook,
        "fb_app_id": fb_app_id,
        "fb_pages": fb_pages,
        "fb_publisher": fb_publisher,
        "configure_twitter": configure_twitter,
        "twitter_site": twitter_site,
        "twitter_author": twitter_author,
        "twitter_type": twitter_type,
        "default_image_url": default_image_url,
    }

    copy_template_files(
        source_dir=source_dir, dest_dir=project_dir, template_context=template_context
    )

    print_success("django-meta is installed successfully.")


@app.command()
def remove():
    """
    Remove django-meta package
    """
    print_step("Removing django-meta package ...")
    if has_dependency("django-meta"):
        subprocess.check_call(["uv", "remove", "django-meta"])

    settings_path = Path.joinpath(get_packages_settings_path(), "django_meta.py")
    settings_path.unlink(missing_ok=True)

    print_success("django-meta is removed successfully.")
