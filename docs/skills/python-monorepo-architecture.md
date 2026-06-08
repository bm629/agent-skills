# python-monorepo-architecture

> The **cross-package** architecture discipline for a multi-package Python
> uv-workspace monorepo — a shared internal library plus one or more app/CLI
> members that depend on it. It owns the decisions that live *between* packages:
> the lib/app boundary, the acyclic depend-inward dependency direction, the
> import-isolation discipline uv cannot enforce, each member's public API at the
> boundary, cross-member test layout, and safely extracting shared code out of
> an existing package. It is the layer ABOVE intra-package module architecture
> (`python-project-structure`) and owns the uv-workspace wiring the `uv` skill
> does not cover.

**Skill file:** [`skills/python-monorepo-architecture/SKILL.md`](../../skills/python-monorepo-architecture/SKILL.md)
**Version:** 1.0.0

## Purpose

Gives an agent the structural decisions a senior engineer applies when a Python
repository grows from one package into several — so the workspace stays an
acyclic, depend-inward graph instead of a tangle of cross-imports. Examples are
uv-workspace flavored, but the dependency-direction and boundary principles are
general. It is the sibling-above of `python-project-structure` (what's *inside*
a package) and references the `uv` skill for general uv usage, while owning the
*workspace* wiring (`[tool.uv.workspace]`, `[tool.uv.sources] {workspace=true}`)
that the `uv` skill does not carry.

## When to activate

- ✅ Deciding whether to split a codebase into a shared `libs/<core>` plus
  `apps/<app>` / `tools/<cli>` members, or keep it one package.
- ✅ Wiring a uv workspace where one member depends on another (the shared lib).
- ✅ Diagnosing or preventing a circular import / tangled dependency between packages.
- ✅ Extracting shared logic out of an app or CLI package into a new shared library.
- ✅ Deciding a member's public API at the package boundary, and how consumers import it.

### When NOT to activate

- Intra-package work — module layout, `__all__`, package `__init__` exports → `python-project-structure`.
- General uv usage — adding a dependency, running a script, the lockfile → the `uv` skill.
- A repo with one deployable and no shared code — a single package is correct.
- A JS/pnpm or Cargo workspace — this skill is Python + uv specific.

## Workflow

Seven steps, each with an opinionated default:

| Step | Decision |
|---|---|
| 1 Split? | Split only for real reuse across deployables or an independently-testable core; **don't** split for conflicting deps / separate venvs / divergent `requires-python` (those aren't one workspace) |
| 2 Wire | `[tool.uv.workspace] members` globs; a member depends on another via `[tool.uv.sources] { <name> = { workspace = true } }` (editable); one shared `uv.lock`; `--package` targets a member; path-dep fallback |
| 3 Direction | acyclic **depend-inward** DAG: apps → shared lib, **never** app ↔ app, the lib depends on no app |
| 4 Enforce | uv can't stop a cross-member import ("Python lacks dependency isolation") → boundary by convention + review; optional `import-linter` contract (Independence + Layers/Forbidden) in CI |
| 5 Boundary API | consumers import a member's public surface (`__init__`/`__all__`), never its `_internal` modules; src-layout per member |
| 6 Tests | per-member `tests/` + `conftest.py`; share fixtures via a test-support package + `pytest_plugins`, not duplicated conftests |
| 7 Extract | safety-net-first: green suite → move modules → repoint imports → suite still green; break a surfaced cycle by pushing down / inverting, never an upward import |

## Hard rules it enforces

- The cross-package graph is a **DAG that points inward**: apps → shared lib, never app ↔ app, and the lib depends on no app.
- A member declares **its own** dependencies; never rely on a sibling's transitive install.
- Consumers import another member through its **public API**, never its `_internal` modules.
- A member depends on another via `[tool.uv.sources] { <name> = { workspace = true } }`; if members can't share one environment / `requires-python`, it is **not** a workspace (path dep or separate repos).
- Extraction is **safety-net-first**; a surfaced cycle is broken by pushing code down, never by an upward import.

## Progressive disclosure (`references/`)

- `references/worked-example.md` — a full three-member workspace walkthrough (root + shared lib + two apps with the `pyproject.toml` edges), an example `.importlinter` contract (Independence + Forbidden/Layers), and a step-by-step safe-extraction with cycle-breaking.
- `references/sources.md` — research provenance (uv official workspace docs, Tweag / pydevtools / Graphite monorepo guides, import-linter + pytest docs).

## Limitations

- **Cross-package layer only** — intra-package module architecture is `python-project-structure`'s job; general uv usage is the `uv` skill's.
- **uv-workspace centric** — the principles (DAG, depend-inward) are general, but tool-specific build graphs (Pants/Bazel/Nx) are out of scope.
- **Python + uv only** — JS/pnpm and Cargo workspaces are out of scope.

## License

MIT — part of the [`agent-skills`](https://github.com/bm629/agent-skills) collection.
