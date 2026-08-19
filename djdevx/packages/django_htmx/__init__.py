import re
from pathlib import Path

from .._base import BasePackage
from djdevx.utils.templates.load_tags import LoadTagManager
from djdevx.utils.types.pixi_types import PixiPackageSpec
from .._registry import register


@register
class DjangoHtmxPackage(BasePackage):
    name: str = "django-htmx"
    display_name: str = "Django HTMX"
    pixi_packages: list[PixiPackageSpec] = [PixiPackageSpec("django-htmx")]

    @property
    def _base_template_path(self) -> Path:
        return self.structure.base_template

    def _add_htmx_snippets(self) -> None:
        path = self._base_template_path
        content = path.read_text()

        content = LoadTagManager.add_load_tag(content, "django_htmx")

        if "{% htmx_script %}" not in content:
            content = content.replace(
                "{% block extra_head %}",
                "{% htmx_script %}\n    {% block extra_head %}",
            )

        body_pattern = re.compile(r"(<body[^>]*)>")
        if "hx-headers=" not in content:

            def add_hx_headers(match: re.Match) -> str:
                tag = match.group(1)
                return (
                    f'{tag} hx-headers=\'{{"X-CSRFToken": "{{{{ csrf_token }}}}"}}\'>'
                )

            content = body_pattern.sub(add_hx_headers, content)

        path.write_text(content)

    def _remove_htmx_snippets(self) -> None:
        path = self._base_template_path
        content = path.read_text()

        content = LoadTagManager.remove_load_tag(content, "django_htmx")

        content = content.replace("{% htmx_script %}\n    ", "")
        content = content.replace("{% htmx_script %}\n", "")
        content = content.replace("{% htmx_script %}", "")

        content = re.sub(
            r'\s+hx-headers=\'{"X-CSRFToken": "{{ csrf_token }}"}\'',
            "",
            content,
        )

        path.write_text(content)

    def after_copy_templates(self) -> None:
        self._add_htmx_snippets()

    def before_pixi_remove(self) -> None:
        self._remove_htmx_snippets()
