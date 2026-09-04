"""Peer integration engine.

When an installable is added or removed (via ``Installable.add`` /
``Installable.remove``), this engine syncs it with its installed peers in
both directions, so the same hooks run no matter which side was installed
first:

- PULL — an installable gets its ``on_peer_added`` for each peer it reacts
  to that is already installed.
- PUSH — installed installables that react to a newly added one get their
  ``on_peer_added`` / ``on_peer_removed``.
- Peer pixi packages declared in ``peer_pixi_packages`` are reconciled
  against the current tracking state and added/removed idempotently.

Interest is declared via keys in ``peer_pixi_packages``. An empty list
value ({ref: []}) is a valid hook-only declaration.
"""

import functools
from pathlib import Path
from typing import Any, Callable, Iterator, Optional

from djdevx.core.console import print_console
from djdevx.core.paths import ProjectStructure
from ..utils.tracking import ProjectTracking

from .ops.pixi import PixiOps
from .registry import Registry, all_registries
from .resolver import resolve
from .ops.scaffold import remove_empty_parents
from .models import PEER_TEMPLATES_DIRNAME
from ..utils.templates.manager import TemplateManager
from .ops.tracking import get_section
from .models import InstallableConfig, InstallableRef
from ..utils.types.pixi_types import PixiPackageSpec

_syncing = False


def _guard(fn):
    """Module-level recursion guard — a hook installing something won't re-sync."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        global _syncing
        if _syncing:
            return
        _syncing = True
        try:
            fn(*args, **kwargs)
        finally:
            _syncing = False

    return wrapper


def call_peer(
    ref: InstallableRef,
    method: str,
    *,
    default: Any = None,
    registries: Optional[list[Registry]] = None,
    **kwargs: Any,
) -> Any:
    """Call *method* on an installed peer instance.

    Returns *default* when the peer is not installed or not registered
    (resolver KeyError is swallowed — unregistered peers are soft).
    """
    registries = registries if registries is not None else all_registries()
    project = ProjectTracking()
    if not project.is_installed(ref.kind.section, ref.name):
        return default
    try:
        cls = resolve(ref, registries)
    except KeyError:
        return default
    fn = getattr(cls(name=ref.name), method, None)
    if not callable(fn):
        return default
    return fn(**kwargs)


def _safe_hook(hook: Callable[..., Any], context: str, **kwargs) -> None:
    """Run a peer hook, isolating failures so one raising hook doesn't abort."""
    try:
        hook(**kwargs)
    except Exception as exc:
        print_console.warning(f"Peer integration hook failed ({context}): {exc}")


def _installed_variants(project: ProjectTracking, cls: type, name: str) -> list[str]:
    return project.get_variants(get_section(cls), name)


# ── Interest and spec helpers ──────────────────────────────────────────────────


def _all_interests(
    installable: InstallableConfig,
    variant=None,
    installed_variant_names: list[str] | None = None,
) -> set[InstallableRef]:
    """Peer refs this installable reacts to, across base, optional variant,
    and optional pre-looked-up installed variant names."""
    interests: set[InstallableRef] = set(installable.peer_pixi_packages.keys())
    extras: list[Any] = []
    if variant is not None:
        extras.append(variant)
    if installed_variant_names is not None:
        extras.extend(installable.variants.get(n) for n in installed_variant_names)
    for v in extras:
        if v is not None and hasattr(v, "peer_pixi_packages"):
            interests.update(v.peer_pixi_packages.keys())
    return interests


def _all_specs(
    installable: InstallableConfig,
    variant=None,
    installed_variant_names: list[str] | None = None,
) -> dict[str, PixiPackageSpec]:
    """Flatten peer specs across base, optional *variant*, and optional
    pre-looked-up *installed_variant_names*."""
    specs: dict[str, PixiPackageSpec] = {}
    for _ref, package_specs in installable.peer_pixi_packages.items():
        for spec in package_specs:
            specs[_spec_key(spec)] = spec
    extras: list[Any] = []
    if variant is not None:
        extras.append(variant)
    if installed_variant_names is not None:
        extras.extend(installable.variants.get(n) for n in installed_variant_names)
    for v in extras:
        if v is not None and hasattr(v, "peer_pixi_packages"):
            for _ref, package_specs in v.peer_pixi_packages.items():
                for spec in package_specs:
                    specs[_spec_key(spec)] = spec
    return specs


def _read_applied(project: ProjectTracking, installable: InstallableConfig) -> set[str]:
    return project.get_applied_peers(installable.section, installable.name)


def _write_applied(
    project: ProjectTracking, installable: InstallableConfig, keys: set[str]
) -> None:
    project.set_applied_peers(installable.section, installable.name, keys)


def _spec_key(spec: PixiPackageSpec) -> str:
    """Stable toml-friendly identity key for a PixiPackageSpec."""
    feature = f":{spec.pixi_feature}" if spec.pixi_feature else ""
    return f"{spec.kind}:{spec.name}{feature}"


def _installed_variant_names(
    project: ProjectTracking, installable: InstallableConfig
) -> list[str]:
    """Return installed variant names for *installable* from tracking."""
    return project.get_variants(installable.section, installable.name)


# ── Reconciliation ─────────────────────────────────────────────────────────────


def _sync_peer_packages(
    installable: InstallableConfig,
    root: Path,
    project: ProjectTracking,
    variant=None,
) -> None:
    """Ensure pixi packages match current installed peers.

    Reconciles declared ``peer_pixi_packages`` against tracking state:
    adds packages for peers that are present, removes packages whose peer
    has left. Stale entries (present in metadata but no longer declared)
    are silently cleaned up without crashing.
    """
    installed_var_names = []
    if variant is not None:
        installed_var_names = [variant.name]
    else:
        installed_var_names = _installed_variant_names(project, installable)

    all_specs = _all_specs(
        installable, variant=None, installed_variant_names=installed_var_names
    )

    desired_keys: set[str] = set()
    for peer_ref, package_specs in installable.peer_pixi_packages.items():
        if project.is_installed(peer_ref.kind.section, peer_ref.name):
            for spec in package_specs:
                desired_keys.add(_spec_key(spec))
    for v in (
        [variant]
        if variant is not None
        else [installable.variants.get(n) for n in installed_var_names]
    ):
        if v is not None and hasattr(v, "peer_pixi_packages"):
            for peer_ref, package_specs in v.peer_pixi_packages.items():
                if project.is_installed(peer_ref.kind.section, peer_ref.name):
                    for spec in package_specs:
                        desired_keys.add(_spec_key(spec))

    stored_applied = _read_applied(project, installable)
    to_add = desired_keys - stored_applied
    to_remove = stored_applied - desired_keys

    if not to_add and not to_remove:
        return

    pixi_ops = PixiOps(root)
    declared_keys = set(all_specs.keys())
    safe_to_remove = to_remove & declared_keys
    if safe_to_remove:
        pixi_ops.remove_packages([all_specs[k] for k in safe_to_remove])
    if to_add:
        pixi_ops.add_packages([all_specs[k] for k in to_add])

    _write_applied(project, installable, desired_keys)


def _remove_peer_packages_for_ref(
    installable: InstallableConfig,
    root: Path,
    project: ProjectTracking,
    peer_ref: InstallableRef,
    variant=None,
) -> None:
    """Remove *installable*'s peer packages declared for *peer_ref*.

    Called by the UNWIND path of ``sync_on_remove`` so that when a peer
    leaves, every listener's packages declared for it drop out regardless
    of what was previously recorded as applied.
    """
    installed_var_names = []
    if variant is not None:
        installed_var_names = [variant.name]
    else:
        installed_var_names = _installed_variant_names(project, installable)

    all_specs = _all_specs(
        installable, variant=None, installed_variant_names=installed_var_names
    )
    removed_keys: set[str] = set()
    for ref, package_specs in installable.peer_pixi_packages.items():
        if ref == peer_ref:
            for spec in package_specs:
                removed_keys.add(_spec_key(spec))
    for v in (
        [variant]
        if variant is not None
        else [installable.variants.get(n) for n in installed_var_names]
    ):
        if v is not None and hasattr(v, "peer_pixi_packages"):
            for ref, package_specs in v.peer_pixi_packages.items():
                if ref == peer_ref:
                    for spec in package_specs:
                        removed_keys.add(_spec_key(spec))

    removed = [all_specs[k] for k in removed_keys if k in all_specs]
    if removed:
        PixiOps(root).remove_packages(removed)

    stored = _read_applied(project, installable)
    stored -= removed_keys
    _write_applied(project, installable, stored)


# ── Template helpers ───────────────────────────────────────────────────────────


def copy_peer_templates(installable, peer) -> None:
    """Copy *installable*'s peer templates authored for *peer* into the project.

    Listeners author their peer-facing payloads under
    ``templates/peer_templates/<peer-name>/``; on a sync the matching subtree
    (e.g. otel's ``peer_templates/postgres/``) is rendered into the project
    root. *installable* is always the template owner, *peer* the subject.
    """
    peer_template_dir = installable.template_dir / PEER_TEMPLATES_DIRNAME / peer.name
    if not peer_template_dir.exists():
        return
    manager = TemplateManager()
    manager.copy_templates(
        source_dir=peer_template_dir,
        dest_dir=installable.structure.root,
        template_context=installable._install_context.copy(),
    )


def cleanup_peer_templates(installable, peer) -> None:
    """Remove the copies of *installable*'s templates authored for *peer*."""
    peer_template_dir = installable.template_dir / PEER_TEMPLATES_DIRNAME / peer.name
    if not peer_template_dir.exists():
        return
    manager = TemplateManager()
    for rel_path in manager.scan_templates(
        source_dir=peer_template_dir,
        template_context=installable._install_context.copy(),
    ):
        full_path = installable.structure.root / rel_path
        if full_path.exists():
            full_path.unlink()
            remove_empty_parents(installable.structure.root, full_path)


def cleanup_all_peer_templates(installable) -> None:
    """Remove all peer-specific templates copied into the project root."""
    interests = _all_interests(installable)
    for peer_ref in interests:
        try:
            peer_cls = resolve(peer_ref, all_registries())
            peer = peer_cls(name=peer_ref.name)
            cleanup_peer_templates(installable, peer)
        except KeyError:
            continue


# ── Engine entry points ────────────────────────────────────────────────────────


def _installed_listeners(
    registries: list[Registry],
    project: ProjectTracking,
    my_ref: InstallableRef,
) -> Iterator[InstallableConfig]:
    """Yield instances of installed installables that react to me."""
    for registry in registries:
        section = registry.kind.section
        for listener_name in sorted(project.list(section)):
            listener_ref = InstallableRef(name=listener_name, kind=registry.kind)
            if listener_ref == my_ref:
                continue
            try:
                listener_cls = registry.get(listener_name)
            except KeyError:
                continue
            listener = listener_cls(name=listener_name)
            installed = project.get_variants(listener.section, listener.name)
            if any(
                interest == my_ref
                for interest in _all_interests(
                    listener, installed_variant_names=installed
                )
            ):
                yield listener


@_guard
def sync_on_add(
    installable: InstallableConfig,
    variant=None,
    *,
    registries: Optional[list[Registry]] = None,
    project_root: Optional[Path] = None,
) -> None:
    """Sync peer integrations after *installable* has been installed and tracked.

    PULL — peers already installed that I react to get my ``on_peer_added``
    (once per installed variant of the peer), then my peer packages are
    reconciled once.
    PUSH — installed listeners that react to me get their ``on_peer_added``.
    """
    registries = registries if registries is not None else all_registries()
    root = Path(project_root) if project_root is not None else ProjectStructure().root
    project = ProjectTracking(root)

    my_ref = installable.ref

    # PULL — peers that arrived earlier
    pulled = False
    for interest in _all_interests(installable, variant):
        for peer_name in sorted(project.list(interest.kind.section).keys()):
            peer_ref = InstallableRef(name=peer_name, kind=interest.kind)
            if peer_ref != interest or peer_ref == my_ref:
                continue
            try:
                peer_cls = resolve(interest, registries)
            except KeyError:
                continue
            peer = peer_cls(name=peer_name)
            variants = _installed_variants(project, peer_cls, peer_name)
            peer_variants = [peer.variants.get(v) for v in variants] or [None]
            hook_kwargs = {"peer": peer, "variant": None}
            for v in peer_variants:
                hook_kwargs["variant"] = v
                _safe_hook(
                    installable.on_peer_added,
                    f"{installable.name} <- {peer.name}",
                    **hook_kwargs,
                )
            copy_peer_templates(installable, peer)
            pulled = True

    if pulled:
        _sync_peer_packages(installable, root, project, variant=variant)

    # PUSH — listeners that arrived earlier
    for listener in _installed_listeners(registries, project, my_ref):
        _safe_hook(
            listener.on_peer_added,
            f"{listener.name} <- {installable.name}",
            peer=installable,
            variant=variant,
        )
        copy_peer_templates(listener, installable)
        _sync_peer_packages(listener, root, project)


@_guard
def sync_on_remove(
    installable: InstallableConfig,
    variant=None,
    applied: Optional[set[str]] = None,
    *,
    registries: Optional[list[Registry]] = None,
    project_root: Optional[Path] = None,
    fully_removed: bool = True,
) -> None:
    """Sync peer integrations after *installable* (or a variant) was removed.

    UNWIND — installed listeners that react to me get their
    ``on_peer_removed``; on full removal their peer packages are reconciled
    too (peers now gone, so those packages drop out).
    SELF-CLEANUP — on full removal, every engine-managed package recorded for
    me goes away with me, regardless of peer state. A variant-only removal
    leaves both my records and my applied peer packages intact.
    """
    registries = registries if registries is not None else all_registries()
    root = Path(project_root) if project_root is not None else ProjectStructure().root
    project = ProjectTracking(root)

    my_ref = installable.ref

    # UNWIND — listeners still installed that are interested in me
    for listener in _installed_listeners(registries, project, my_ref):
        _safe_hook(
            listener.on_peer_removed,
            f"{listener.name} x {installable.name}",
            peer=installable,
            variant=variant,
        )
        cleanup_peer_templates(listener, installable)
        if fully_removed:
            # The peer is gone, so drop its packages from the listener and
            # record the removal in the listener's applied metadata.
            _remove_peer_packages_for_ref(listener, root, project, my_ref)

    # SELF-CLEANUP
    if fully_removed:
        declared = _all_specs(installable, variant=None)
        if applied is not None:
            # Only packages that were actually applied go away with me.
            to_remove = [declared[k] for k in applied if k in declared]
            if to_remove:
                PixiOps(root).remove_packages(to_remove)
        else:
            # Legacy/direct call without applied info: full cleanup.
            if declared:
                PixiOps(root).remove_packages(list(declared.values()))
        cleanup_all_peer_templates(installable)


__all__ = ["call_peer", "sync_on_add", "sync_on_remove"]
