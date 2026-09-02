"""Template and file scaffolding operations for installables."""

import shutil
from pathlib import Path
from ..templates.manager import TemplateManager

from .types import PEER_TEMPLATES_DIRNAME


def resolve_template_source(installable, variant=None) -> Path | None:
    if variant and variant.template_path:
        return installable.template_dir / variant.template_path
    if installable.template_path:
        return installable.template_dir / installable.template_path
    if installable.template_dir.exists():
        return installable.template_dir
    return None


def copy_templates(installable, variant=None) -> None:
    manager = TemplateManager()
    context = installable._install_context.copy()
    source_dir = resolve_template_source(installable, variant)
    if source_dir is None:
        return
    if source_dir.exists():
        manager.copy_templates(
            source_dir=source_dir,
            dest_dir=installable.structure.root,
            template_context=context,
            exclude_dirs=[PEER_TEMPLATES_DIRNAME],
        )


def template_output_files(installable, variant=None) -> list[Path]:
    source_dir = resolve_template_source(installable, variant)
    if source_dir is None or not source_dir.exists():
        return []
    manager = TemplateManager()
    context = installable._install_context.copy()
    return manager.scan_templates(
        source_dir=source_dir,
        template_context=context,
        exclude_dirs=[PEER_TEMPLATES_DIRNAME],
    )


def remove_empty_parents(root: Path, file_path: Path) -> None:
    current = file_path.parent
    while current != root and current.exists() and not any(current.iterdir()):
        current.rmdir()
        current = current.parent


def cleanup_files(installable, variant=None) -> None:
    files = template_output_files(installable, variant)
    for rel_path in files:
        full_path = installable.structure.root / rel_path
        if full_path.exists():
            full_path.unlink()
        remove_empty_parents(installable.structure.root, full_path)

    extras = variant if variant else installable
    for rel_path in extras.files_to_remove:
        (installable.structure.root / rel_path).unlink(missing_ok=True)
    for rel_path in extras.folders_to_remove:
        shutil.rmtree(installable.structure.root / rel_path, ignore_errors=True)


def restore_original_templates(installable) -> None:
    manager = TemplateManager()
    for project_rel, template_rel in installable.restore_on_remove.items():
        source = installable.new_templates_dir / template_rel
        dest = installable.structure.root / project_rel
        if source.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            manager.copy_template(
                source_file=source,
                dest_dir=dest.parent,
            )
