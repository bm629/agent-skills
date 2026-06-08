---
name: python-monorepo-architecture
description: >
  Use when architecting or splitting a Python repository into a multi-package
  uv-workspace monorepo — a shared internal library plus one or more app or CLI
  members that depend on it — and you need the cross-package boundaries right:
  which code becomes a shared lib vs an app member, the acyclic depend-inward
  dependency direction (apps depend on the core lib, never on each other), the
  import-isolation discipline uv cannot enforce, each member's public API at the
  package boundary, cross-member test layout, and safely extracting shared code
  out of an existing package. Covers uv workspace wiring (members,
  tool.uv.sources, single lockfile, --package) and composes with the uv and
  python-project-structure skills. Keywords: monorepo, uv workspace,
  multi-package, shared library, package boundaries, dependency direction,
  circular import, import-linter.
extensions:
  claude:
    when_to_use: "Designing/splitting a Python repo into multiple uv-workspace members, deciding a lib/app boundary, fixing a cross-package import cycle, or extracting shared code into a lib."
  copilot: {}
  cursor: {}
  gemini: {}
  codex: {}
version: "1.0.0"
forge:
  status: reviewed
  forged: 2026-06-08
  reviewed: 2026-06-08
---

# `python-monorepo-architecture` — SKILL.md

> **Variant:** standard · **When to use:** architecting the cross-package structure of a multi-package Python uv-workspace monorepo.

## Overview

This skill is about the **cross-package** layer of a Python monorepo: a single repository holding several installable packages (members) managed by a uv workspace — typically one shared library plus one or more application or CLI members that build on it. It covers the decisions that live *between* packages: where the lib/app boundary goes, which way dependencies are allowed to point, how to keep the boundary honest when the tool can't, what each member exposes to the others, where shared tests live, and how to carve a shared library out of an existing package without breaking it. It does **not** re-teach intra-package module layout (`__all__`, layered structure — that is the `python-project-structure` skill) or general uv usage (`uv add`/`uv run` — the `uv` skill); it *owns* the uv-workspace wiring because those skills do not cover it, and it composes with both.

## When to activate

- ✅ Deciding whether to split a growing codebase into a shared `libs/<core>` plus `apps/<app>` / `tools/<cli>` members, or keep it one package.
- ✅ Wiring a uv workspace where one member depends on another (the shared library).
- ✅ Diagnosing or preventing a circular import / tangled dependency between packages.
- ✅ Extracting shared logic out of an app or CLI package into a new shared library.
- ✅ Deciding what a member's public API at the package boundary should be, and how consumers import it.

**Do NOT activate when:**

- The work is *inside one package* — module layout, `__all__`, package `__init__` exports → use `python-project-structure`.
- The work is general uv usage — adding a dependency, running a script, the lockfile → use the `uv` skill.
- The repo has one deployable and no shared code to factor out — a single package is correct; splitting it is premature (see Anti-patterns).
- It is a JS/pnpm or Cargo workspace — this skill is Python + uv specific.

## Workflow

### Step 1: Decide whether to split at all

Split into multiple members only when there is **genuinely shared code consumed by two or more deployables**, or a deployable that benefits from an independently-testable core. Signals to split: two apps (e.g. a CLI and a web service) both need the same domain logic; one app is a thin shell over reusable logic. Signals **not** to split:

- One deployable, no reuse — keep one package.
- Members would need **conflicting dependency versions** or **separate virtual environments** — a uv workspace shares one environment and one lockfile, so this is the case where you use a **path dependency** instead of a workspace member (see Step 2), or separate repos.
- Members need **different `requires-python`** — a uv workspace enforces a single `requires-python` (the intersection of all members), so divergent Python floors don't fit one workspace.

A typical shape, once you do split:

```
repo/
  pyproject.toml          # workspace root: [tool.uv.workspace] members
  libs/core/              # shared library member  (package: core)
  apps/api/               # web service member     (package: api) -> depends on core
  apps/cli/               # CLI member             (package: cli) -> depends on core
```

### Step 2: Wire the uv workspace (this skill owns this)

In the **root** `pyproject.toml`, declare members as globs:

```toml
[tool.uv.workspace]
members = ["libs/*", "apps/*"]
exclude = ["libs/scratch"]      # optional
```

Every directory matched by `members` (and not `exclude`d) must contain its own `pyproject.toml`. A member depends on another member by naming it as a normal dependency **and** marking the source as the workspace:

```toml
# apps/api/pyproject.toml
[project]
dependencies = ["core"]

[tool.uv.sources]
core = { workspace = true }     # resolve `core` from the workspace, not PyPI; editable
```

Key mechanics:

- One **shared `uv.lock`** and one virtual environment for the whole workspace. `uv lock` operates on the entire workspace; `uv run` / `uv sync` default to the root and take `--package <member>` to target one member.
- Workspace dependencies are **editable** — an edit in `core` is immediately visible to `api` with no reinstall.
- `[tool.uv.sources]` at the **root** applies to all members; a member's own `[tool.uv.sources]` overrides it.
- **Fallback:** when members can't share one environment, use a **path dependency** (`core = { path = "../../libs/core" }`) or separate them — not a workspace.

(For `uv add`/`uv run`/lockfile basics see the `uv` skill; for a member's *internal* module layout see `python-project-structure`.)

### Step 3: Fix the dependency direction — depend inward, stay acyclic

The package-dependency graph must be a **DAG**, and it must point **inward** toward the shared core:

- Apps/CLIs depend **on** the shared library: `api → core`, `cli → core`.
- Apps **never** depend on each other: no `api → cli`, no `cli → api`.
- The shared library depends on **neither** app — `core` has no app dependency. Shared code that "needs" something from an app is a sign that thing belongs *in* core (or in another lib), not that core should import upward.

A cross-app or upward import is the anti-pattern: it creates a cycle (directly or transitively) and couples deployables that should ship independently. If two apps need to share something new, push it **down** into `core` (or a second lib), don't import sideways.

### Step 4: Keep the boundary honest — uv can't enforce it

A uv workspace shares one environment, and **Python has no dependency isolation**: nothing at runtime stops a member from importing a package (or module) that a *sibling* member declared. uv itself states it "can't ensure that packages don't import dependencies declared by another workspace member." So the boundary is kept by **convention + code review**, not by the tool:

- Treat a sideways/upward import (Step 3) as a **review-blocking** defect.
- Declare every dependency a member actually uses in **that member's** `pyproject.toml` — never lean on a sibling's transitive install.
- **Optional automated enforcement — `import-linter`.** It checks a `.importlinter` contract in CI / a pre-commit hook and fails the build on a forbidden import. The two contract types that express these rules:
  - **Independence** — "these modules don't import each other" → the apps are mutually independent (no `api ↔ cli`).
  - **Layers** / **Forbidden** — a layered order (apps above `core`) or "`core` is forbidden from importing the apps" → enforces depend-inward.

  Keep it a thin safety net; the rules above stand with or without it.

### Step 5: Define each member's public API at the boundary

A consumer imports a member through that member's **public surface** — its package `__init__` / `__all__` — and treats everything else as internal. So:

- Export the shared library's intended API from `libs/core/src/core/__init__.py` (with `__all__`); consumers do `from core import X`.
- Apps depend on that boundary, **not** on `core`'s `_internal` modules — reaching into another member's private modules re-couples you to its internals and defeats the split.
- (The intra-package `__all__` / underscore-privacy mechanics are the `python-project-structure` skill's domain — this skill adds only the cross-member rule: *consume the boundary, not the internals*.)

Use a **src layout per member** (`libs/core/src/core/`, `apps/api/src/api/`) so tests run against the installed package, not a stray top-level import — consistent across members.

### Step 6: Place tests and shared fixtures

- Each member owns its `tests/` with its own `conftest.py`; pytest auto-discovers fixtures per directory.
- For fixtures **genuinely shared across members**, prefer one of: a small **shared test-support package** (its own member, or a `tests/fixtures/` module) loaded via `pytest_plugins`, rather than copy-pasted conftests. Keep a fixture as close as possible to what it represents; only truly repo-wide fixtures belong at the top.
- Don't reach across members' `tests/` directories directly; share through the support package.

### Step 7: Extract shared code safely (when splitting an existing package)

Carving a library out of an existing app is a **behavior-preserving refactor — safety-net-first**:

1. Ensure the existing test suite is green first (it is your net).
2. Create the new `libs/<core>` member (Step 2) and wire the app to depend on it.
3. **Move** the shared modules into `core` (move, don't rewrite); repoint the app's imports to `from core import …`.
4. Run the **full existing suite** — it must stay green with the same test count. Move the moved modules' unit tests into `libs/core/tests/`.
5. If the move surfaces a **cycle** (the moved code imported back into the app, or the app needs something the lib now also needs), break it by moving the shared dependency down into `core` too, or inverting the dependency (pass the app-specific piece in as a parameter / via an interface) — never satisfy it with an upward import.

See `references/worked-example.md` for a full three-member walkthrough (root + lib + two apps), the `.importlinter` contract, and a step-by-step extraction.

## Rules

**Hard rules (never violate):**

- The cross-package dependency graph is a **DAG that points inward**: apps → shared lib, never app ↔ app, and the shared lib depends on no app.
- A member declares **its own** dependencies; never rely on a sibling member's transitive install.
- Consumers import another member through its **public API** (`__init__`/`__all__`), never its `_internal` modules.
- A member depends on another via `[tool.uv.sources] { <name> = { workspace = true } }`; if members can't share one environment / `requires-python`, it is **not** a workspace (use a path dep or separate repos).
- Extraction is **safety-net-first**: existing suite green → move → repoint imports → suite still green; a surfaced cycle is broken by pushing code down, never by an upward import.

**Preferences (override-able):**

- Use a **src layout** per member for consistent, install-based test discovery.
- Add an **`import-linter`** contract (Independence + Layers/Forbidden) to enforce the boundary in CI once more than one app exists.
- Share fixtures via a **test-support package** + `pytest_plugins`, not duplicated conftests.
- Keep the member set small; add a member only for a real deployable or real reuse.

## Gotchas

- **uv won't stop a bad import.** The workspace shares one venv, so `from cli import …` inside `api` *works at runtime* even though it violates the architecture — uv can't catch it. Only review (or `import-linter`) will. Don't assume "it imports, so it's allowed."
- **Single `requires-python` for the whole workspace.** uv takes the intersection across members; a member that needs a higher Python floor silently raises the floor for everyone (or doesn't fit the workspace). Decide the Python floor at the workspace level.
- **Reaching into a sibling's internals.** `from core._internal.thing import x` compiles and runs, but re-couples you to private structure that can change without notice. Import only the boundary.
- **Splitting too early.** A two-member workspace for code with no actual reuse adds lockfile + wiring + boundary overhead for nothing. Split when reuse or an independently-testable core is real, not speculatively.
- **The extraction that turns green-but-wrong.** After moving modules, a still-green suite can hide a new *upward* import you added to make it pass. Check the dependency direction explicitly after the move, not just the test result.
- **Forgetting `[tool.uv.sources]`.** Listing `core` in `dependencies` without the `{ workspace = true }` source makes uv try to resolve it from PyPI — it'll fail or grab a stranger's package. The source line is what makes it a workspace dep.

## Anti-patterns

- **"I'll just import the other app's helper."** A sideways `app → app` import to reuse one function. Push the helper **down** into the shared lib instead; sideways imports cycle and couple deployables.
- **"The lib can import from the app just this once."** Any upward (lib → app) import inverts the DAG. The thing the lib needs belongs in the lib (or is passed in), never fetched upward.
- **"It's all one venv anyway, so boundaries don't matter."** The shared environment is a convenience, not a license to cross boundaries — it's exactly why discipline + review are required.
- **"Let me split every module into its own package."** Over-decomposition: a package per module multiplies pyproject/boundary overhead. A member is a *deployable or a genuinely shared library*, not every folder.
- **"Reach into `_internal` to avoid widening the public API."** If a consumer needs it, expose it on the boundary deliberately; importing privates is hidden coupling.

## Output

The artifact is a **decision + structure**: a member topology (which packages exist and why), the root + per-member `pyproject.toml` wiring (`[tool.uv.workspace]` + `[tool.uv.sources]`), a stated acyclic depend-inward dependency direction, each member's public-API boundary, a test/fixture layout, and — when refactoring — a safety-net-first extraction sequence. The consumer is the engineer or coding agent building or restructuring the workspace; the structure it produces is what later feature work builds on.

## Related

- `uv` — general uv usage (`uv add`, `uv run`, the lockfile). This skill owns the *workspace* wiring the `uv` skill doesn't cover; reach for `uv` for everything non-workspace.
- `python-project-structure` — *intra-package* module architecture, `__all__`, layered structure. This skill is the *cross-package* layer above it; use them together (this one for the member boundary, that one for what's inside a member).
- `import-linter` (external tool) — optional CI enforcement of the boundary via `.importlinter` contracts.

## Progressive disclosure

- `references/worked-example.md` — a full three-member workspace walkthrough (root + shared lib + two apps with the `pyproject.toml` edges), an example `.importlinter` contract (Independence + Layers), and a step-by-step safe-extraction. Load when building or restructuring a concrete workspace.
- `references/sources.md` — research provenance / citations.

## Body budget

- `description` ≤ 1,024 chars. Claude truncates combined `description` + `when_to_use` at 1,536 chars in the listing.
- Body ≤ ~500 lines / 5,000 tokens.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k tokens, error >50k.
