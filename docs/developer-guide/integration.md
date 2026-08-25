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

Two class attributes on every installable (inherited by variants):

```python
from djdevx.utils.installable.types import (
    ConditionalPackage, InstallableRef, FRAMEWORK, FEATURE,
)
from djdevx.utils.installable import when_peer

class MyPackage(BasePackage):
    # Peers I react to via hooks. Only needed when you override the
    # on_peer_added / on_peer_removed hooks — package gates below are
    # picked up automatically.
    listens_to: list[InstallableRef] = [
        InstallableRef(name="bootstrap", kind=FRAMEWORK),
    ]

    # Pixi packages gated behind a condition
    conditional_packages: list[ConditionalPackage] = [
        ConditionalPackage(
            package=PixiPackageSpec("opentelemetry-instrumentation-psycopg", kind="pypi"),
            when=when_peer(InstallableRef("opentelemetry", FEATURE)),
        )
    ]
```

| Declaration | Description |
|-------------|-------------|
| `InstallableRef(name, kind)` | Interested in a specific peer (name normalized `_` -> `-` at construction) |
| `ConditionalPackage(package, when)` | One pixi package the engine adds while `when` holds and removes when it does not |

An installable **reacts to** a peer if it names the peer in `listens_to` *or*
gates a package on it with `when_peer(...)` — the engine derives interests
from both, deduplicated. In short: `when_peer` alone is enough for package
sync; add `listens_to` only when hooks are involved too.

### Conditions

`when` is any callable receiving a single `ConditionContext`:

- `ctx.installable` — the owning installable instance (and `ctx.variant` when
  evaluating variant-scoped conditionals),
- `ctx.project` — a `ProjectTracking`, created lazily on first access.

```python
from djdevx.utils.installable import when_peer

# Peer present (primary use case)
when=when_peer(InstallableRef("opentelemetry", FEATURE))

# Driven by install params / instance config
def _needs_celery(ctx) -> bool:
    return ctx.installable.use_celery

# Combining peer state with instance config
def _when_otel_and_async(ctx) -> bool:
    return (
        ctx.project.is_installed(FEATURE.section, "opentelemetry")
        and ctx.installable.async_mode
    )
```

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
`remove()` **after** untracking, so gates evaluate against the new state.

```
sync_on_add(installable, variant)
  PULL:   my interests × installed peers  → my.on_peer_added(peer, v)
          (once per installed variant of the peer)
          + reconcile my gated packages against tracking state (once per sync)
  PUSH:   installed listeners × me        → listener.on_peer_added(me)
          + reconcile their gated packages

sync_on_remove(installable, variant, fully_removed)
  UNWIND:        interested installed peers → peer.on_peer_removed(me)
                 + on full removal, engine reconciles their conditional
                 packages (gates on me now fail → those packages drop out)
  SELF-CLEANUP:  on full removal, every engine-recorded package of mine
                 goes away with me
```

### Semantics

- **Matching** — an interest matches a peer when the `InstallableRef`s are
  equal (kind and normalized name; `_` → `-`, same rule as the Registry).
- **Order independence** — PULL covers "I came later", PUSH covers "they came
  later". Both orders trigger the identical `on_peer_added`.
- **Cross-category** — the push/unwind scan covers all five registries
  (packages, features, frameworks, databases, caches), so frameworks ↔ packages
  ↔ features integrate freely.
- **Removal** — the leaving installable is untracked first, then peers are
  unwound. A *full* removal additionally reconciles listeners' gates and drops
  the owner's recorded packages. Removing just one variant of a multi-variant
  installable keeps it installed: hooks still fire (with the removed `variant`
  passed through) so templates can adapt, but gated packages and their records
  stay untouched.
- **Listener self-cleanup** — when the *listening* side is fully removed, the
  engine removes every pixi package it added via `conditional_packages`
  (recorded in `extra_packages`) — nobody else would clean them up.

## Conditional packages & `extra_packages` tracking

When integration fires, the engine automatically:

1. `pixi add`s each `conditional_packages` entry whose `when` condition holds,
2. records the specs as `extra_packages = [...]` in the listener's own
   `[<section>.<name>]` tracking entry in `djdevx.toml`.

On unwind or self-cleanup it `pixi remove`s them and clears the recorded list.
This keeps cleanup correct even when things are removed out of order.

```toml
[database.postgres]
installed = true
display_name = "Postgres"
extra_packages = ["opentelemetry-instrumentation-psycopg"]
```

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
- **Composability** — `needs` and peer interests (`listens_to` / `when_peer`)
  are orthogonal and may point at the same peer: `needs` auto-installs a hard
  dependency *before* me; interests adapt my artifacts to an optional presence
  *without* installing it.

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

### allauth × bootstrap (both orders)

`AllauthPackage.listens_to = [InstallableRef("bootstrap", FRAMEWORK)]`, with framework-styled
overlay templates inside the owning installable:
`django_allauth/templates/account/frameworks/bootstrap/**`.

- Framework installed first → PULL copies overlays over base account output.
- Allauth installed first → PUSH after bootstrap's `add()` calls
  `allauth.on_peer_added(bootstrap)` — identical code path.
- Framework removed → UNWIND calls `allauth.on_peer_removed(bootstrap)`,
  which re-copies base templates over the styled ones.

### otel × postgres (both orders)

`PostgresDatabase.listens_to = [InstallableRef("opentelemetry", FEATURE)]`, plus
`conditional_packages = [ConditionalPackage(package=PixiPackageSpec("opentelemetry-instrumentation-psycopg", kind="pypi"), when=when_peer(...))]`.

`on_peer_added(otel)` writes instrumentation settings; `on_peer_removed(otel)`
removes them. OTel never needs to know its providers — no reverse dependency.
Removing either side cleans up both settings and pixi packages.

## Related

- [Installable System](installable-system.md) — shared infrastructure overview
- [Common Concepts](creating-an-installable.md#peer-integration) — Peer Integration quick start
- [Add a Package](adding-a-package.md#peer-integration) — package-specific example
- [Add a Feature](adding-a-feature.md#peer-integration) — feature-specific example
