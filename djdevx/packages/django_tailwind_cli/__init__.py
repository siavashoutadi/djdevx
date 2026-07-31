import re

from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from .._registry import register


@register
class DjangoTailwindCliPackage(BasePackage):
    name: str = "django-tailwind-cli"
    display_name: str = "Django Tailwind CLI"
    pixi_packages: list[PixiPackageSpec] = [
        PixiPackageSpec("django-tailwind-cli", kind="pypi")
    ]

    def after_copy_templates(self) -> None:
        self._add_dark_mode_include()
        self._update_gitignore()
        self._update_dockerfile()

    def before_pixi_remove(self) -> None:
        self._remove_dark_mode_include()
        self._cleanup_gitignore()
        self._cleanup_dockerfile()

    @property
    def _base_template_path(self):
        return self.structure.base_template

    def _add_dark_mode_include(self) -> None:
        path = self._base_template_path
        if not path.exists():
            return
        content = path.read_text()
        include_str = "{% include './_tw_dark_mode.html' %}"
        if include_str not in content:
            content = content.replace(
                "<body>",
                f"<body>\n    {include_str}",
            )
            path.write_text(content)

    def _remove_dark_mode_include(self) -> None:
        path = self._base_template_path
        if not path.exists():
            return
        content = path.read_text()
        include_str = "{% include './_tw_dark_mode.html' %}"
        content = re.sub(
            r"\s*" + re.escape(include_str) + r"\s*\n?",
            "",
            content,
        )
        path.write_text(content)

    def _update_gitignore(self) -> None:
        path = self.structure.gitignore_path
        if not path.exists():
            return
        content = path.read_text()
        if "tailwind" not in content.lower():
            content += "\n# Tailwind\nnode_modules/\n"
            path.write_text(content)

    def _cleanup_gitignore(self) -> None:
        path = self.structure.gitignore_path
        if not path.exists():
            return
        content = path.read_text()
        if "node_modules/" in content:
            content = content.replace("\n# Tailwind\nnode_modules/\n", "")
            content = content.replace("# Tailwind\nnode_modules/\n", "")
            content = content.replace("node_modules/\n", "")
        path.write_text(content)

    def _update_dockerfile(self) -> None:
        path = self.structure.dockerfile_path
        if not path.exists():
            return
        content = path.read_text()
        if "tailwind" not in content.lower():
            content += "\n# Tailwind\n"
            path.write_text(content)

    def _cleanup_dockerfile(self) -> None:
        path = self.structure.dockerfile_path
        if not path.exists():
            return
        content = path.read_text()
        if "# Tailwind" in content:
            content = content.replace("# Tailwind\n", "")
        path.write_text(content)
