"""DjangoSnakeoilPackage — SEO meta tags management."""

from .._base import BasePackage
from djdevx.utils.templates.load_tags import LoadTagManager
from djdevx.utils.types.pixi_types import PixiPackageSpec
from ....utils.installable.types import InstallParam
from .._registry import register


@register
class DjangoSnakeoilPackage(BasePackage):
    name: str = "django-snakeoil"
    display_name: str = "Django Snakeoil"
    pixi_packages: list[PixiPackageSpec] = [
        PixiPackageSpec("django-snakeoil", kind="pypi")
    ]

    install_params: list[InstallParam] = [
        InstallParam(
            name="site_name",
            help="Display name of your website for og:site_name meta tag (e.g., 'My Blog')",
            prompt="Please enter your site name",
        ),
        InstallParam(
            name="site_description",
            help="Default description for your website (shown in search results and social shares)",
            prompt="Please enter your site description (leave empty to skip)",
        ),
        InstallParam(
            name="author",
            help="Default author name for meta author tag",
            prompt="Please enter default author name (leave empty to skip)",
        ),
        InstallParam(
            name="og_type",
            default="website",
            help="OpenGraph type for og:type meta tag (website, article, blog). See: https://ogp.me/#types",
            prompt="Please enter OpenGraph type (website/article/blog)",
        ),
        InstallParam(
            name="default_image_url",
            default="images/logo.svg",
            help="Full URL to default share image for social media (1200x630px recommended)",
            prompt="Enter default image URL for social sharing (or press Enter for images/logo.svg)",
        ),
        InstallParam(
            name="site_url",
            help="Your website's full URL including protocol (e.g., 'https://example.com')",
            prompt="Please enter your site URL (e.g., https://example.com, leave empty to skip)",
        ),
        InstallParam(
            name="locale",
            help="Default locale/language for og:locale (e.g., 'en_US', 'en_GB', 'es_ES')",
            prompt="Please enter your site locale (e.g., en_US, leave empty to skip)",
        ),
        InstallParam(
            name="twitter_site",
            help="Twitter/X handle for your website (e.g., '@yoursite')",
            prompt="Please enter your Twitter/X handle (e.g., @yoursite, leave empty to skip)",
        ),
        InstallParam(
            name="twitter_card_type",
            default="summary_large_image",
            help="Twitter card type: 'summary' or 'summary_large_image' (recommended for rich previews)",
            prompt="Please enter Twitter card type (summary/summary_large_image)",
        ),
        InstallParam(
            name="keywords",
            help="Default keywords for SEO (comma-separated, e.g., 'django, web development, python')",
            prompt="Please enter default keywords (comma-separated, leave empty to skip)",
        ),
    ]

    def after_copy_templates(self, step=None) -> None:
        self._add_snakeoil_snippets()

    def before_pixi_remove(self, step=None) -> None:
        self._remove_snakeoil_snippets()

    def _add_snakeoil_snippets(self) -> None:
        base_template_path = self.structure.base_template
        content = base_template_path.read_text()

        if "{% load snakeoil %}" in content and "{% meta %}" in content:
            return

        content = LoadTagManager.add_load_tag(content, "snakeoil")

        if "{% meta %}" not in content:
            viewport_marker = (
                '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
            )
            if viewport_marker in content:
                content = content.replace(
                    viewport_marker, viewport_marker + "\n    {% meta %}"
                )

        base_template_path.write_text(content)

    def _remove_snakeoil_snippets(self) -> None:
        base_template_path = self.structure.base_template
        content = base_template_path.read_text()

        content = LoadTagManager.remove_load_tag(content, "snakeoil")

        new_lines = []
        removed = False
        for line in content.split("\n"):
            if "{% meta %}" in line:
                removed = True
                continue
            new_lines.append(line)

        if removed:
            base_template_path.write_text("\n".join(new_lines))
