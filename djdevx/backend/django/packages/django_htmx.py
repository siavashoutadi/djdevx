import re

from ._base import BasePackage


class DjangoHtmxPackage(BasePackage):
    name = "django-htmx"
    packages = ["django-htmx"]

    def after_copy_templates(self) -> None:
        self._add_htmx_snippets()

    def after_uv_remove(self) -> None:
        self._remove_htmx_snippets()

    def _add_htmx_snippets(self) -> None:
        """Add HTMX script and CSRF headers to base template."""
        pm = self.pm
        base_template = pm.base_template_path
        content = base_template.read_text()

        if "{% load django_htmx %}" not in content:
            content = "{% load django_htmx %}\n" + content

        if "{% htmx_script %}" not in content:
            content = content.replace("</head>", "  {% htmx_script %}\n  </head>")

        if "hx-headers=" not in content:
            body_pattern = r"<body([^>]*)>"
            replacement = r'<body\1 hx-headers=\'{"x-csrftoken": "{{ csrf_token }}"}\'>'
            content = re.sub(body_pattern, replacement, content)

        base_template.write_text(content)

    def _remove_htmx_snippets(self) -> None:
        """Remove HTMX script and CSRF headers from base template."""
        pm = self.pm
        base_template = pm.base_template_path
        content = base_template.read_text()

        content = content.replace("{% load django_htmx %}\n", "")
        content = content.replace("  {% htmx_script %}\n", "")
        hx_headers_pattern = (
            r' hx-headers=\\?\'{"x-csrftoken": "{{ csrf_token }}"}\\?\'(?=[\s>])'
        )
        content = re.sub(hx_headers_pattern, "", content)

        base_template.write_text(content)


_pkg = DjangoHtmxPackage(__file__)
app = _pkg.app
