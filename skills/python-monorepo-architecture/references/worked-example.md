# Worked example — a three-member uv-workspace monorepo

A concrete instance of the `python-monorepo-architecture` method: one shared
library and two apps, wired with uv, enforced with `import-linter`, plus a
step-by-step extraction. Names are generic (`core`/`api`/`cli`) — substitute
your own.

## Target layout

```
repo/
  pyproject.toml                 # workspace root
  uv.lock                        # one shared lockfile (whole workspace)
  .importlinter                  # optional boundary enforcement
  libs/
    core/
      pyproject.toml             # package: core
      src/core/
        __init__.py              # the public API (with __all__)
        _internal/…              # private; consumers must not import this
      tests/
  apps/
    api/
      pyproject.toml             # package: api  -> depends on core
      src/api/…
      tests/
    cli/
      pyproject.toml             # package: cli  -> depends on core
      src/cli/…
      tests/
```

Dependency direction (a DAG, pointing inward):

```
api ─┐
     ├─▶ core        # never api ↔ cli ; core depends on neither
cli ─┘
```

## Root `pyproject.toml`

```toml
[project]
name = "repo-workspace"
version = "0"
requires-python = ">=3.12"       # one floor for the whole workspace (uv takes the intersection)

[tool.uv.workspace]
members = ["libs/*", "apps/*"]
# exclude = ["libs/scratch"]
```

## Member `pyproject.toml` (an app depending on the lib)

```toml
# apps/api/pyproject.toml
[project]
name = "api"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
  "core",                        # the shared library member
  "fastapi",                     # api-only third-party deps live here
]

[tool.uv.sources]
core = { workspace = true }      # resolve from the workspace (editable), not PyPI

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

`apps/cli/pyproject.toml` is the same shape (depends on `core`, plus its own
CLI deps). `libs/core/pyproject.toml` declares **only** core's own deps and
**no** app dependency.

Common commands (workspace-aware):

```bash
uv sync                          # resolve the whole workspace into one env
uv run --package api  pytest     # run a single member's work
uv run --package core pytest
uv lock                          # one lockfile, whole workspace
```

## The shared library's public boundary

```python
# libs/core/src/core/__init__.py
from core._models import Order, Customer
from core._service import place_order, load_customer

__all__ = ["Order", "Customer", "place_order", "load_customer"]
```

Consumers import the boundary, never the privates:

```python
# apps/api/src/api/routes.py
from core import place_order             # ✅ the public API
# from core._service import _helper      # ❌ reaching into internals — forbidden
```

## Optional enforcement — `.importlinter`

uv cannot stop a forbidden import; this contract fails CI if one appears.
Install `import-linter`, run `lint-imports` (e.g. in CI or a pre-commit hook).

```ini
[importlinter]
root_packages =
    core
    api
    cli

[importlinter:contract:apps-are-independent]
name = Apps do not import each other
type = independence
modules =
    api
    cli

[importlinter:contract:core-imports-no-app]
name = The shared library never imports an app
type = forbidden
source_modules =
    core
forbidden_modules =
    api
    cli
```

- The **independence** contract encodes "no `api ↔ cli`" (even indirectly).
- The **forbidden** contract encodes "`core` never imports upward into an app."
  (A **layers** contract — `api`/`cli` above `core` — expresses the same
  depend-inward order if you prefer that form.)

## Step-by-step: extracting `core` out of an existing app

Starting point: everything lives in `apps/cli` and a second app (`api`) now
needs the same domain logic. Carve out `core` — safety-net-first.

1. **Green first.** `uv run --package cli pytest` passes. That suite is the net.
2. **Create the lib member.** Scaffold `libs/core/` with its `pyproject.toml`
   + `src/core/` + `tests/`; add `libs/*` to the root `members` if not already
   matched. `uv sync`.
3. **Wire the consumer.** Add `core` to `apps/cli`'s `dependencies` +
   `[tool.uv.sources] core = { workspace = true }`.
4. **Move, don't rewrite.** Move the shared modules from `apps/cli/src/cli/…`
   into `libs/core/src/core/…` (a file move). Define `core`'s public API in
   `__init__.py`. Repoint the CLI's imports: `from cli.domain import X` →
   `from core import X`.
5. **Re-run the net.** `uv run pytest` across the workspace must be green with
   the same test count. Move the moved modules' unit tests into
   `libs/core/tests/`.
6. **Check direction, not just green.** Confirm no new upward/sideways import
   crept in to make it pass — `core` must import nothing from `cli`/`api`. If
   `lint-imports` is set up, it asserts this.
7. **Point the second app at the lib.** `apps/api` now depends on `core` the
   same way; both apps share one source of truth, neither imports the other.

### Breaking a cycle the move exposes

If, after the move, `core` seems to need something from the app (e.g. the CLI's
config object), don't import upward. Options:

- **Push it down:** if the dependency is itself shared, move it into `core`
  (or a second lib) too.
- **Invert it:** have the app **pass** the app-specific piece into the `core`
  function (a parameter, or an interface/protocol `core` defines and the app
  implements). The dependency now points inward again.
