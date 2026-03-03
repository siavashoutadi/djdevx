import fileinput
from pathlib import Path

from ._base import BasePackage


class DjangoTailwindCliPackage(BasePackage):
    name = "django-tailwind-cli"
    packages = ["django-tailwind-cli"]

    def install(self) -> None:
        """Install and configure django-tailwind-cli."""
        self._uv_add_all()
        self._copy_templates()
        self._add_tailwind_snippets()
        self._add_input_css_to_git_ignore()
        self._add_tailwind_build_to_docker_file()

    def remove(self) -> None:
        """Remove django-tailwind-cli."""
        self._remove_tailwind_snippets()
        self._remove_input_css_to_git_ignore()
        self._remove_tailwind_build_to_docker_file()
        self._cleanup_tailwind_files()
        super().remove()

    def _add_tailwind_snippets(self) -> None:
        """Add tailwind tags to base template."""
        base_template = self.pm.base_template_path
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

    def _remove_tailwind_snippets(self) -> None:
        """Remove tailwind tags from base template."""
        base_template = self.pm.base_template_path
        with fileinput.input(files=[base_template], inplace=True) as f:
            for line in f:
                if (
                    "{% load tailwind_cli %}" not in line
                    and "{% tailwind_css %}" not in line
                    and '{% include "./_tw_dark_mode.html" %}' not in line
                ):
                    print(line, end="")

    def _add_input_css_to_git_ignore(self) -> None:
        """Add tailwind CSS to .gitignore."""
        ignore_line = "/static/css/tailwind.min.css"
        git_ignore = self.pm.gitignore_path
        content = git_ignore.read_text()

        if ignore_line not in content:
            content = content + ignore_line

        git_ignore.write_text(content)

    def _remove_input_css_to_git_ignore(self) -> None:
        """Remove tailwind CSS from .gitignore."""
        git_ignore = self.pm.gitignore_path
        with fileinput.input(files=[git_ignore], inplace=True) as f:
            for line in f:
                if "/static/css/tailwind.min.css" not in line:
                    print(line, end="")

    def _add_tailwind_build_to_docker_file(self) -> None:
        """Add tailwind build command to Dockerfile."""
        build_static_line = "uv run manage.py collectstatic --noinput && \\"
        tailwind_build_line = "uv run manage.py tailwind build --force && \\"

        docker_file = self.pm.dockerfile_path
        content = docker_file.read_text()

        if tailwind_build_line not in content:
            content = content.replace(
                build_static_line, tailwind_build_line + "\n    " + build_static_line
            )

        docker_file.write_text(content)

    def _remove_tailwind_build_to_docker_file(self) -> None:
        """Remove tailwind build command from Dockerfile."""
        docker_file = self.pm.dockerfile_path
        with fileinput.input(files=[docker_file], inplace=True) as f:
            for line in f:
                if "uv run manage.py tailwind build" not in line:
                    print(line, end="")

    def _cleanup_tailwind_files(self) -> None:
        """Clean up tailwind-specific configuration and CSS files."""
        tailwind_config = Path.joinpath(self.pm.project_path, "tailwind.config.js")
        tailwind_config.unlink(missing_ok=True)

        tailwind_css_input = Path.joinpath(
            self.pm.project_path, "tailwind", "src", "css", "input.css"
        )
        tailwind_css_input.unlink(missing_ok=True)

        tailwind_css_output = Path.joinpath(
            self.pm.project_path, "static", "css", "tailwind.min.css"
        )
        tailwind_css_output.unlink(missing_ok=True)

        tailwind_dark_mode = Path.joinpath(
            self.pm.project_path, "templates", "_tw_dark_mode.html"
        )
        tailwind_dark_mode.unlink(missing_ok=True)


_pkg = DjangoTailwindCliPackage(__file__)
app = _pkg.app
