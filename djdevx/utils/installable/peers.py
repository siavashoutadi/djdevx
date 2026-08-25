"""Peer integration engine.

When an installable is added or removed (via ``Installable.add`` /
``Installable.remove``), this engine syncs it with its installed peers in
both directions, so the same hooks run no matter which side was installed
first:

- PULL — an installable gets its ``on_peer_added`` for each peer it reacts
  to that is already installed.
- PUSH — installed installables that react to a newly added one get their
  ``on_peer_added`` / ``on_peer_removed``.
- Conditional packages gated by ``when_peer`` are reconciled against the
  current tracking state and recorded under ``extra_packages``.

An installable "reacts to" a peer if the peer is named in ``listens_to``
(needed for hooks) *or* appears in any ``when_peer`` gate (package sync
works from gates alone — no ``listens_to`` required).
"""

import functools
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterator, Optional

from ..console.print import print_console
from ..project.project_structure import ProjectStructure
from ..tracking import ProjectTracking

from .pixi_ops import PixiOps
from .registry import Registry, all_registries
from .resolver import resolve
from .tracking import get_section
from .types import (
    ConditionContext,
    InstallableConfig,
    InstallableRef,
)

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


@dataclass(frozen=True)
class PeerCheck:
    """``when`` condition gating packages on whether a peer is installed.

    Carries its ``InstallableRef`` so the engine can derive the owner's peer
    interests straight from ``conditional_packages`` — ``listens_to`` is only
    needed when hooks are used as well.
    """

    ref: InstallableRef

    def __call__(self, ctx: ConditionContext) -> bool:
        return ctx.project.is_installed(self.ref.kind.section, self.ref.name)


def when_peer(ref: InstallableRef) -> PeerCheck:
    """Build a condition gating packages on a peer installable.

    The package is included exactly while *ref* is tracked as installed.
    """
    return PeerCheck(ref)


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


def _set_extra_packages(
    project: ProjectTracking, cls: type, name: str, packages: set[str]
) -> None:
    section = get_section(cls)
    project.add(section, name, metadata={"extra_packages": sorted(packages)})


def _reconcile_gated_packages(
    owner: InstallableConfig,
    root: Path,
    project: ProjectTracking,
) -> None:
    """Make owner's engine-managed pixi packages match its current gates.

    Packages whose gate passes but aren't applied yet are added; recorded
    packages whose gate no longer passes are pixi-removed. The recorded set
    (``extra_packages`` in tracking) is the source of truth for what the
    engine manages, so gates that flip back and forth stay consistent.
    """
    section = get_section(type(owner))
    recorded = set(project.list(section).get(owner.name, {}).get("extra_packages", []))
    specs_by_name = {c.package.name: c.package for c in owner.conditional_packages}
    ctx = ConditionContext(owner, project=project)
    passing = {c.package.name for c in owner.conditional_packages if c.when(ctx)}

    fresh = sorted(passing - recorded)
    stale = sorted(recorded - passing)
    if not fresh and not stale:
        return

    pixi_ops = PixiOps(root)
    if fresh:
        pixi_ops.add_packages([specs_by_name[name] for name in fresh])
    if stale:
        pixi_ops.remove_packages([specs_by_name[name] for name in stale])

    _set_extra_packages(project, type(owner), owner.name, passing)


def _drop_gated_packages(
    owner: InstallableConfig,
    root: Path,
    project: ProjectTracking,
) -> None:
    """Remove every engine-managed package of an owner being fully removed."""
    section = get_section(type(owner))
    recorded = sorted(
        project.list(section).get(owner.name, {}).get("extra_packages", [])
    )
    if not recorded:
        return
    specs_by_name = {c.package.name: c.package for c in owner.conditional_packages}
    removable = [specs_by_name[n] for n in recorded if n in specs_by_name]
    if removable:
        PixiOps(root).remove_packages(removable)
    _set_extra_packages(project, type(owner), owner.name, set())


def _interests_of(installable: InstallableConfig) -> list[InstallableRef]:
    """Peer refs this installable reacts to: ``listens_to`` plus any gates.

    Deduplicated, order preserved, so a ref declared both ways triggers
    hooks exactly once.
    """
    gate_refs = [
        c.when.ref
        for c in installable.conditional_packages
        if isinstance(c.when, PeerCheck)
    ]
    return list(dict.fromkeys([*installable.listens_to, *gate_refs]))


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
            if any(interest == my_ref for interest in _interests_of(listener)):
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
    (once per installed variant of the peer), then my gated packages are
    reconciled once.
    PUSH — installed listeners that react to me get their ``on_peer_added``.
    """
    registries = registries if registries is not None else all_registries()
    root = project_root if project_root is not None else ProjectStructure().root
    project = ProjectTracking(root)

    my_ref = installable.ref

    # PULL — peers that arrived earlier
    pulled = False
    for interest in _interests_of(installable):
        for peer_name in sorted(project.list(interest.kind.section)):
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
            for v in peer_variants:
                _safe_hook(
                    installable.on_peer_added,
                    f"{installable.name} <- {peer.name}",
                    peer=peer,
                    variant=v,
                )
            pulled = True

    if pulled:
        _reconcile_gated_packages(installable, root, project)

    # PUSH — listeners that arrived earlier
    for listener in _installed_listeners(registries, project, my_ref):
        _safe_hook(
            listener.on_peer_added,
            f"{listener.name} <- {installable.name}",
            peer=installable,
            variant=variant,
        )
        _reconcile_gated_packages(listener, root, project)


@_guard
def sync_on_remove(
    installable: InstallableConfig,
    variant=None,
    *,
    registries: Optional[list[Registry]] = None,
    project_root: Optional[Path] = None,
    fully_removed: bool = True,
) -> None:
    """Sync peer integrations after *installable* (or a variant) was removed.

    UNWIND — installed listeners that react to me get their
    ``on_peer_removed``; on full removal their gated packages are reconciled
    too (gates on me now fail, so those packages drop out).
    SELF-CLEANUP — on full removal, every engine-managed package recorded for
    me goes away with me, regardless of gate state. A variant-only removal
    leaves both my records and my applied gated packages intact.
    """
    registries = registries if registries is not None else all_registries()
    root = project_root if project_root is not None else ProjectStructure().root
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
        if fully_removed:
            _reconcile_gated_packages(listener, root, project)

    # SELF-CLEANUP
    if fully_removed:
        _drop_gated_packages(installable, root, project)


__all__ = ["call_peer", "sync_on_add", "sync_on_remove", "when_peer"]
