import fileinput
import shutil
from pathlib import Path
from typing import List, Optional

from jinja2 import Environment, FileSystemLoader


class TemplateManager:
    """
    Generic template and file operations manager.
    Handles Jinja2 template rendering and file copying operations.
    """

    @staticmethod
    def render_template_string(template_str: str, template_context: dict) -> str:
        """
        Render a Jinja2 template string with the given context.

        Args:
            template_str: Template string that may contain Jinja2 syntax
            template_context: Context variables for template rendering

        Returns:
            Rendered string
        """
        if "{{" in template_str or "{%" in template_str:
            template = Environment().from_string(template_str)
            return template.render(**template_context)
        return template_str

    def copy_templates(
        self,
        source_dir: Path,
        dest_dir: Path,
        template_context: Optional[dict] = None,
        exclude_files: Optional[List[Path]] = None,
    ) -> None:
        """
        Copy template files from source to destination with Jinja2 processing.

        Args:
            source_dir: Source directory containing templates
            dest_dir: Destination directory for processed files
            template_context: Context variables for template rendering
            exclude_files: List of file patterns to exclude from copying
        """
        if template_context is None:
            template_context = {}
        if exclude_files is None:
            exclude_files = []

        dest_dir.mkdir(parents=True, exist_ok=True)
        jinja_env = Environment(loader=FileSystemLoader(source_dir))

        for source_path in source_dir.rglob("*"):
            if any(source_path.match(str(exclude)) for exclude in exclude_files):
                continue

            rel_path = source_path.relative_to(source_dir)

            rendered_parts = [
                self.render_template_string(part, template_context)
                for part in rel_path.parts
            ]
            dest_path = dest_dir / Path(*rendered_parts)

            if source_path.is_dir():
                dest_path.mkdir(parents=True, exist_ok=True)
            else:
                if source_path.suffix == ".j2":
                    filename = self.render_template_string(
                        dest_path.stem, template_context
                    )
                    dest_path = dest_path.parent / filename
                    template = jinja_env.get_template(str(rel_path))
                    rendered_content = template.render(**template_context)
                    rendered_content = rendered_content.rstrip("\n") + "\n"

                    dest_path.write_text(rendered_content)
                else:
                    filename = self.render_template_string(
                        dest_path.name, template_context
                    )
                    dest_path = dest_path.parent / filename

                    shutil.copy2(source_path, dest_path)

    def copy_template(
        self, source_file: Path, dest_dir: Path, template_context: Optional[dict] = None
    ) -> Path:
        """
        Copy a single template file with Jinja2 processing.

        Args:
            source_file: Source file to copy
            dest_dir: Destination directory
            template_context: Context variables for template rendering

        Returns:
            Path to the created file
        """
        if template_context is None:
            template_context = {}

        dest_dir.mkdir(parents=True, exist_ok=True)

        jinja_env = Environment(loader=FileSystemLoader(source_file.parent))

        filename = self.render_template_string(source_file.name, template_context)
        dest_path = dest_dir / filename

        if source_file.suffix == ".j2":
            template = jinja_env.get_template(source_file.name)
            rendered_content = template.render(**template_context)
            rendered_content = rendered_content.rstrip("\n") + "\n"

            if dest_path.suffix == ".j2":
                dest_path = dest_path.with_suffix("")

            dest_path.write_text(rendered_content)
        else:
            shutil.copy2(source_file, dest_path)

        return dest_path

    @staticmethod
    def remove_lines_from_file(file_path: Path, patterns_to_remove: List[str]) -> None:
        """
        Remove lines from a file that match any of the given patterns.

        Args:
            file_path: Path to the file to modify
            patterns_to_remove: List of string patterns to remove
        """
        with fileinput.input(files=[file_path], inplace=True) as f:
            for line in f:
                if not any(pattern in line for pattern in patterns_to_remove):
                    print(line, end="")
