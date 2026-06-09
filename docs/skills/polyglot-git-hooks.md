# polyglot-git-hooks

> Set up Git hooks for a polyglot or monorepo project with Lefthook — one
> `lefthook.yml` running fast format/lint on staged files at `pre-commit` and
> slower type-check/test gates at `pre-push`, across mixed-language subtrees
> (e.g. a TypeScript subtree and a Python subtree), in parallel. Covers install +
> activation (incl. the fresh-clone problem), the `lefthook.yml` schema
> (`commands`/`jobs`, `glob`, `root`, `run` with `{staged_files}`/`{push_files}`,
> `stage_fixed`, `skip`/`only`, `parallel`), a genuinely polyglot worked example,
> the hooks-vs-CI division of labor (incl. no-CI-yet), and the `--no-verify`
> bypass. Teaches the wiring; defers tool flags to `biome`/`ruff`/`ty`/
> `typescript-typecheck` and the pipeline to `turborepo`. Lefthook 2.x.

**Skill file:** [`skills/polyglot-git-hooks/SKILL.md`](../../skills/polyglot-git-hooks/SKILL.md)
**Version:** 1.0.0

## Purpose

Gives an agent one language-agnostic `lefthook.yml` that drives the *right* fast
checks on staged files at `pre-commit` and the slower gates at `pre-push`, across
a mixed Python + TypeScript repo, in parallel — the local "fail fast before the
commit/push" layer that complements (not replaces) CI. The skill is named for its
differentiator (cross-language hooks from one config); the tool it teaches is
**Lefthook**. It owns the hook *wiring* — the per-tool details belong to their own
skills, which it references.

## When to activate

- ✅ Setting up Git hooks for a repo (a new `lefthook.yml`), or adding a `pre-commit`/`pre-push` gate.
- ✅ Wiring lint/format/type-check to run on **staged files** before a commit (or push files before a push).
- ✅ Configuring hooks for a **polyglot or monorepo** where subtrees use different toolchains.
- ✅ Migrating off husky+lint-staged or the Python `pre-commit` framework to a single-config polyglot setup.

### When NOT to activate

- Learning/configuring a specific linter/formatter/type-checker — use that tool's skill (`biome`, `ruff`, `ty`, `typescript-typecheck`).
- Designing the CI pipeline — hooks are the *local* gate; CI is separate (`turborepo`).
- Enforcing a `--no-verify` ban as org policy — a narrow policy-hook concern, not hook setup.

## Workflow

| Step | Does |
|---|---|
| 1 Pick Lefthook | A single Go binary, one config, native staged-file filtering — over husky+lint-staged (JS-only, two tools) and the Python `pre-commit` framework (Python-centric). |
| 2 Install + activate | `npm i -D lefthook` (+ its `postinstall`) or a binary, then `lefthook install`; solve fresh-clone via `postinstall`/a `prepare` script. |
| 3 Author the schema | `commands:`/`jobs:`, `glob`, `root` (subtree CWD), `run` + `{staged_files}`/`{push_files}`, `stage_fixed`, `skip`/`only`, `parallel`. |
| 4 Polyglot example | `pre-commit` runs `biome check --write` on staged TS **and** `ruff` on staged Python (scoped, `stage_fixed`, parallel); `pre-push` runs `tsc`/`ty`/tests. |
| 5 Hooks vs CI | Local fast gate vs authoritative CI; **no CI yet → raise the `pre-push` bar** (full type-check + tests). |
| 6 `--no-verify` | Document the bypass (`--no-verify`, `LEFTHOOK=0`); a policy hook to block it is named, not set up. |

## Hard rules it enforces

- **One `lefthook.yml` at the repo root** — a single language-agnostic config is the whole point.
- **`pre-commit` is fast + staged-only** (`{staged_files}` + `stage_fixed`); slow type-check/test gates go to `pre-push`.
- **Scope every command** with `glob` (+ `root` for a subtree) so the right tool runs on the right files.
- **Owns wiring, not tools** — references `biome`/`ruff`/`ty`/`typescript-typecheck` for flags and `turborepo` for the pipeline.
- **Pin the major version** with `min_version:` (current major **Lefthook 2.x**).

## Progressive disclosure (`references/`)

- `references/lefthook-reference.md` — the fuller `lefthook.yml` schema (full option list, the `jobs:`/groups form, global keys, version/migration notes).
- `references/sources.md` — research provenance.

## Limitations

- **Lefthook 2.x** pinned; note the `jobs:` structure was added in v1.10.0 (not a v2-only feature).
- **Hooks are local and bypassable** (`--no-verify`) — CI is the *enforced* gate, not the hook.
- **Owns hook wiring, not the tools or the CI pipeline** — those live in their own skills.

## License

MIT — part of the [`agent-skills`](https://github.com/bm629/agent-skills) collection.
