# Integration Protocol

The Integration Protocol lets installables adapt to each other
**order-independently**: no matter whether A or B was installed first, the same
integration code runs exactly once per pair. It lives in
`utils/installable/peers.py` and is completely generic — packages,
features, frameworks, databases, and caches can all integrate with each other.

## Core design principle

Every installable owns its own artifacts (templates, settings snippets).
Integration never means "write someone else's files" — it means **"re-render my
own artifacts given who else is present."** That single rule makes both install
orders run through one code path.

## Declaration

The sole mechanism to declare peer interest is `peer_pixi_packages`, a dict
mapping an `InstallableRef` to a list of `PixiPackageSpec`. The engine uses
**keys** as interest declarations and **values** as the packages to add or
remove. A key with an empty list (`{ref: []}`) is a valid hook-only
declaration — the engine fires `on_peer_added` / `on_peer_removed` but never
touches pixi packages for that peer.

```python
from djdevx.utils.installable.types import InstallableRef, FRAMEWORK

class MyPackage(BasePackage):
    peer_pixi_packages: dict[InstallableRef, list[PixiPackageSpec]] = {
        # Packages to add/remove when bootstrap is present
        InstallableRef("bootstrap", FRAMEWORK): [
            PixiPackageSpec("some-integration-lib", kind="pypi"),
        ],
        # Hook-only: bootstrap presence triggers hooks, no packages
        InstallableRef("another", FRAMEWORK): [],
    }

    def on_peer_added(self, peer, variant=None) -> None:
        # Adapt artifacts to peer presence
        ...

    def on_peer_removed(self, peer, variant=None) -> None:
        # Revert to base artifacts
        ...
```

| Declaration | Description |
|-------------|-------------|
| `peer_pixi_packages[InstallableRef]` | Packages to add when the peer is installed, remove when it leaves |
| `on_peer_added` / `on_peer_removed` | Optional hooks for custom adaptation (templates, settings) |

The engine automatically syncs these packages during `add` and `remove`.
Interest is determined by the union of keys at the base level and on every
**installed variant** of the installable, so a variant can declare packages
or hooks that only apply when that variant is active.

## Hooks

Override these on your installable:

```python
def on_peer_added(self, peer, variant=None) -> None:
    """Apply peer presence. MUST be idempotent."""

def on_peer_removed(self, peer, variant=None) -> None:
    """Undo peer presence. MUST be idempotent."""
```

- `peer` is a fresh instance of the peer's class.
- `variant` is the peer's `Variant` object when the peer has installed variants,
  otherwise `None`. The engine calls `on_peer_added` **once per installed
  variant** of the peer (allauth with `["account", "mfa"]` installed → two calls).

## Engine phases

`sync_on_add(installable, variant)` runs at the end of `Installable.add()`
(after tracking); `sync_on_remove(installable, variant)` runs at the end of
`remove()` **after** untracking.

```
sync_on_add(installable, variant)
  PULL:   my peer_pixi_packages × installed peers → add packages
          + my.on_peer_added(peer, v) for each peer (once per variant)
  PUSH:   installed listeners × me → listener.on_peer_added(me)
          + add their peer packages

sync_on_remove(installable, variant, fully_removed)
  UNWIND:        interested installed peers → peer.on_peer_removed(me)
                 + remove their peer packages if fully_removed
  SELF-CLEANUP:  remove my peer packages (if fully_removed)
```

### Semantics

- **Matching** — a peer matches when the `InstallableRef`s are equal (kind and
  normalized name; `_` → `-`).
- **Order independence** — PULL covers "I came later", PUSH covers "they came
  later". Both orders trigger the identical `on_peer_added`.
- **Cross-category** — the push/unwind scan covers all five registries
  (packages, features, frameworks, databases, caches).
- **Removal** — the leaving installable is untracked first, then peers are
  unwound (`sync_on_remove` runs after untracking). Removing just one variant
  of a multi-variant installable keeps it installed: hooks still fire (with
  the removed `variant` passed through) so templates can adapt, and
  `peer_pixi_packages` are reconciled across all installed variants.
- **UNWIND on full removal** — when a *peer* is fully removed, every installed
  listener's `peer_pixi_packages` declared **for that peer** are dropped
  (across base and all installed variants of the listener) and removed from
  the listener's `peer_pixi_applied` metadata.
- **SELF-CLEANUP** — on full removal the owner drops its `peer_pixi_packages`
  that were **actually applied** (recorded in `peer_pixi_applied`); a direct /
  legacy call without applied info drops **all** of them. Either way the entry
  is not recreated in `djdevx.toml`.

## Guarantees

- **Error isolation** — a raising hook is caught by the engine, reported via
  `print_console.warning(...)`, and does not abort the triggering add/remove or
  prevent remaining listeners from running. Integration failures are soft.
- **Reentrancy guard** — a module-level recursion guard prevents infinite loops
  if a hook installs something.
- **Idempotency contract** — hooks must be idempotent (check-before-write),
  matching the style used across installables. The engine may call them more
  than once (e.g. once per variant).
- **Unregistered peers are soft** — everywhere the engine looks up a peer
  (pull matching, push scan, `call_peer`), an unregistered name is treated
  exactly like "not installed" and skipped, never fatal.
- **Composability** — `needs` and peer integration are orthogonal: `needs`
  auto-installs a hard dependency *before* me; peer integration adapts my
  artifacts to an optional presence *without* installing it.

## Escape hatch — `call_peer()`

For explicit cross-calls beyond the hook protocol:

```python
from djdevx.utils.installable import call_peer
from djdevx.utils.installable.types import DATABASE, InstallableRef

result = call_peer(InstallableRef("postgres", DATABASE), "collect_metrics", default=None)
```

Resolves the peer via the registry, checks `djdevx.toml`, instantiates it, and
calls the method. Returns `default` when the peer is not installed **or** not
registered.

## Worked examples

### Allauth × bootstrap (both orders)

```python
class AllauthPackage(BasePackage):
    peer_pixi_packages: dict[InstallableRef, list[PixiPackageSpec]] = {
        InstallableRef("bootstrap", FRAMEWORK): [],
    }

    def on_peer_added(self, peer, variant=None) -> None:
        # copy framework-styled overlays over base account output
        ...

    def on_peer_removed(self, peer, variant=None) -> None:
        # revert to base templates
        ...
```

`AllauthPackage` listens for bootstrap and applies styled overlays when it arrives.
Removing bootstrap reverts the templates. The engine handles both installation orders.

### OTel × postgres

`PostgresDatabase` declares `peer_pixi_packages` for OTel:
```python
peer_pixi_packages = {
    InstallableRef("opentelemetry", FEATURE): [
        PixiPackageSpec("opentelemetry-instrumentation-psycopg", kind="pypi")
    ]
}
```
`on_peer_added(otel)` writes instrumentation settings; `on_peer_removed(otel)`
removes them. OTel never needs to know its providers — no reverse dependency.
Removing either side cleans up both settings and peer packages.

## Related

- [Installable System](installable-system.md) — shared infrastructure overview
- [Common Concepts](creating-an-installable.md#peer-integration) — Peer Integration quick start
- [Add a Package](adding-a-package.md#peer-integration) — package-specific example
- [Add a Feature](adding-a-feature.md#peer-integration) — feature-specific example
