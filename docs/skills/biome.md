# biome

> Lint and format a JavaScript/TypeScript project with Biome v2 — the single
> fast Rust tool that lints, formats, and organizes imports, replacing the
> ESLint + Prettier pair (the JS analog of Ruff). Covers installing Biome, the
> `biome.json` config (formatter, linter rule groups + `domains`, the
> assist/import-organize actions, VCS integration, overrides, monorepo
> `extends`), the CLI (`biome check --write`, `biome ci`), migrating from
> ESLint/Prettier, the v1→v2 deltas (`--apply` → `--write`), and authoring custom
> lint rules as GritQL plugins. Defers pipeline task-wiring to `turborepo`.

**Skill file:** [`skills/biome/SKILL.md`](../../skills/biome/SKILL.md)
**Version:** 1.0.0

## Purpose

Gives an agent one fast tool and one `biome.json` in place of the ESLint +
Prettier stack — the JS/TS analog of `ruff`. It sets Biome up, writes a correct
config, runs the right current commands locally and in CI, migrates an existing
ESLint/Prettier setup, steers clear of stale v1 idioms, and authors custom rules
as GritQL plugins. It owns Biome itself; running Biome as a cached pipeline task
is the `turborepo` skill's job.

## When to activate

- ✅ Adding lint + format to a JS/TS project (new or replacing ESLint/Prettier).
- ✅ Writing or fixing a `biome.json` (formatter, linter rules, import organizing, VCS, overrides).
- ✅ Wiring a lint/format CI gate.
- ✅ Migrating from ESLint/Prettier, or authoring a custom rule as a GritQL plugin.

### When NOT to activate

- Wiring Biome as a task in a Turborepo/pnpm pipeline — use the `turborepo` skill.
- A Python project — that's `ruff` (Biome is the JS/TS counterpart).

## Workflow

| Step | Does |
|---|---|
| 1 Install + init | `npm install --save-dev --save-exact @biomejs/biome`; `npx biome init` → `biome.json` |
| 2 Configure | `biome.json`: `formatter`, `linter` (rule groups + `domains`), `assist.actions.source.organizeImports`, `vcs`, `overrides` |
| 3 Run | `biome check --write .` (lint + format + organize, safe fixes); `--write --unsafe` for unsafe |
| 4 CI gate | `biome ci .` — read-only; the analog of `ruff check` |
| 5 Migrate | `biome migrate eslint --write` / `biome migrate prettier --write` |
| 6 Custom rules | register a `.grit` plugin in `plugins`; write the GritQL pattern + `register_diagnostic` |

## Hard rules it enforces

- **Use the v2 CLI** — `--write` / `--write --unsafe`; the v1 `--apply` / `--apply-unsafe` are gone.
- **`biome ci` is the CI gate, not `check --write`** — CI must be read-only.
- **One `biome.json` per project** (`extends` for nested/monorepo); don't run ESLint/Prettier for the same concerns — Biome replaces them.

## Progressive disclosure (`references/`)

- `references/config.md` — the full `biome.json` schema (top-level keys, formatter options, linter rule groups + `domains`, `assist`, `vcs`, `overrides`) and the v2 config-shape changes.
- `references/cli.md` — all commands + flags, the `--write`/`ci` semantics, and the v1→v2 CLI delta table.
- `references/gritql-plugins.md` — authoring a custom rule: registration, GritQL pattern syntax, `register_diagnostic`, a complete example, limitations.
- `references/migration-monorepo.md` — the `migrate` commands + caveats and the `extends`/`root` monorepo model (+ the Turborepo hand-off).
- `references/sources.md` — research provenance.

## Limitations

- **Biome v2** — pinned to the v2.x line; an explicit v1→v2 delta section steers off stale CLI. Confirm the exact current version when installing.
- **GritQL plugins target JS and CSS only** (currently); advanced pattern syntax should be checked against the current docs.
- **Owns Biome, not the pipeline** — running Biome as a cached task is the `turborepo` skill.

## License

MIT — part of the [`agent-skills`](https://github.com/bm629/agent-skills) collection.
