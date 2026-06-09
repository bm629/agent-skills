---
name: biome
description: >
  Use when setting up or running linting and formatting in a JavaScript or
  TypeScript project with Biome — the single fast Rust tool that lints, formats,
  and organizes imports, replacing the ESLint + Prettier pair (the JS analog of
  Ruff). Covers installing Biome v2, the biome.json config (formatter, linter
  rule groups, the assist/import-organize actions, VCS integration, overrides,
  monorepo extends), the CLI (biome check --write, biome ci for CI), migrating
  from ESLint/Prettier, the v1->v2 deltas (e.g. --apply became --write), and
  authoring custom lint rules as GritQL plugins. Use when adding a lint/format
  gate, writing or fixing a biome.json, or porting an ESLint/Prettier setup. Not
  the Turborepo task wiring (compose with that skill).
extensions:
  claude: {}
  copilot: {}
  cursor: {}
  gemini: {}
  codex: {}
version: "1.0.0"
forge:
  status: reviewed
  forged: 2026-06-09
  reviewed: 2026-06-09
---

# `biome` — SKILL.md

> **Variant:** standard · **When to use:** linting and formatting a JS/TS project with Biome v2.

## Overview

Biome is a single Rust binary that lints, formats, and organizes imports for JavaScript, TypeScript, JSX, JSON, CSS, and GraphQL — one tool and one `biome.json` in place of the ESLint + Prettier stack. It is the JS/TS analog of Python's `ruff`: fast, opinionated defaults, one config. This skill covers installing Biome (v2), writing `biome.json`, the current CLI (including the `biome ci` gate), migrating an existing ESLint/Prettier setup, the v1→v2 changes that trip up stale knowledge, and authoring custom lint rules as GritQL plugins. Verified against Biome v2; confirm the exact current version when you install.

## When to activate

- ✅ Adding lint + format to a JS/TS project (new or replacing ESLint/Prettier).
- ✅ Writing or fixing a `biome.json` (formatter, linter rules, import organizing, VCS, overrides).
- ✅ Wiring a lint/format CI gate.
- ✅ Migrating from ESLint/Prettier, or authoring a custom rule as a GritQL plugin.

**Do NOT activate when:**

- You need to wire Biome as a task in a Turborepo/pnpm pipeline — compose with the `turborepo` skill; this skill owns Biome itself, not the task graph.
- The project is Python — that's `ruff` (Biome is the JS/TS counterpart, named here only as the analog).

## Workflow

### Step 1: Install + init

```sh
npm install --save-dev --save-exact @biomejs/biome   # i.e. -D -E
npx biome init                                        # writes biome.json
```

### Step 2: Configure `biome.json`

```jsonc
{
  "$schema": "https://biomejs.dev/schemas/<version>/schema.json",
  "vcs": { "enabled": true, "clientKind": "git", "useIgnoreFile": true },
  "files": { "includes": ["src/**", "!**/dist"] },
  "formatter": { "enabled": true, "indentStyle": "space", "lineWidth": 100 },
  "linter": { "enabled": true, "rules": { "recommended": true } },
  "assist": { "enabled": true, "actions": { "source": { "organizeImports": "on" } } }
}
```

(`biome init` writes `$schema` with the version-pinned URL — don't ship the `<version>` literal.) Full schema — rule groups + `linter.domains`, language blocks, `overrides`, monorepo `extends`/`root` — in [`references/config.md`](references/config.md).

### Step 3: Run it

```sh
npx biome check --write .          # lint + format + organize imports, apply SAFE fixes
npx biome check --write --unsafe . # also apply unsafe fixes
npx biome format --write .         # format only;  npx biome lint .  # lint only
```

`biome check` runs all three (format, lint, import sort). Full command/flag reference + the v1→v2 CLI deltas: [`references/cli.md`](references/cli.md).

### Step 4: CI gate

```sh
npx biome ci .     # read-only: format + lint + import-sort checks, never writes
```

Use `biome ci` in CI (the analog of `ruff check`), never `check --write` (which mutates). Wire it as the lint/format job; defer the pipeline/caching to the `turborepo` skill.

### Step 5: Migrate from ESLint / Prettier (if applicable)

```sh
npx biome migrate eslint --write     # ports .eslintrc / flat config + .eslintignore
npx biome migrate prettier --write   # ports .prettierrc
```

Details + caveats: [`references/migration-monorepo.md`](references/migration-monorepo.md).

### Step 6: Custom rules (optional) — GritQL plugins

Register a `.grit` plugin in `biome.json` `plugins` and write the pattern; full authoring guide (pattern syntax, `register_diagnostic`, a complete example, limitations) in [`references/gritql-plugins.md`](references/gritql-plugins.md). Prefer a built-in rule first; reach for a plugin only when no rule covers the case.

## Rules

**Hard rules (never violate):**

- **Use the v2 CLI.** `--write` / `--write --unsafe` apply fixes; the v1 `--apply` / `--apply-unsafe` are gone. Emitting `--apply` is the #1 stale-knowledge error — see Gotchas.
- **`biome ci` is the CI gate, not `check --write`.** CI must be read-only; `check --write` mutates the tree.
- **One `biome.json` per project** (use `extends` for nested/monorepo configs). Don't also run ESLint/Prettier for the same concerns — Biome replaces them.

**Preferences (override-able):**

- Biome's formatter defaults to **tabs** and a 2-space width with `lineWidth` 80. If the team standardizes on spaces (e.g. coming from Prettier), set `formatter.indentStyle` / `lineWidth` explicitly.
- Enable `vcs.useIgnoreFile` so Biome respects `.gitignore`.
- Start from `rules.recommended` and tighten per rule group as needed.

## Gotchas

- **`--apply` was removed (v1→v2).** v1 used `biome check --apply` / `--apply-unsafe`; v2 uses `--write` / `--write --unsafe` (`--fix` is an alias of `--write`). Stale snippets and old muscle memory emit `--apply`, which now errors. See [`references/cli.md`](references/cli.md).
- **Import organizing moved.** v1's top-level `organizeImports` is gone; in v2 it's an **assist action** under `assist.actions.source.organizeImports`. A v1-shaped config silently won't organize imports.
- **`include`/`ignore` → `includes` (v2).** v2's `files.includes` is a single glob list using `!`-prefixed negations, replacing v1's separate `include`/`ignore`. A v1-shaped `files` block is wrong.
- **Formatter default is tabs.** Prettier users expecting spaces get tabs unless they set `indentStyle: "space"`. `biome migrate prettier` aligns it, but a fresh `biome init` does not.
- **GritQL plugins target JS and CSS only** (currently). A plugin for another language won't run.

## Anti-patterns

- **Running ESLint + Prettier AND Biome for the same files.** Double tooling, conflicting fixes, slower. Biome replaces them — migrate, don't stack.
- **`biome check --write` in CI.** CI mutates the tree and can mask drift. Use `biome ci`.
- **Reaching for a GritQL plugin when a built-in rule exists.** Check the rule groups first; plugins are for genuinely custom checks.
- **Duplicating the Turborepo pipeline here.** Wiring Biome as a cached task belongs to the `turborepo` skill; this skill stops at the Biome command.

## Output

A configured `biome.json` plus the lint/format commands wired locally (`biome check --write`) and in CI (`biome ci`) — optionally migrated from an ESLint/Prettier setup and extended with custom GritQL rules. The consumer is the developer workflow and the CI gate that enforce a consistent, lint-clean codebase.

## Related

- `turborepo` — run `biome ci`/`check` as a cached pipeline task; this skill owns Biome, that one owns the task graph.
- `vite` — the build the linted/formatted code typically ships in.
- `ruff` — the Python lint+format analog Biome mirrors conceptually (different tool).

## Progressive disclosure

- `references/config.md` — load when writing `biome.json`: full top-level schema, formatter/linter/assist options, rule groups, `overrides`, monorepo `extends`/`root`, and the v2 config-shape changes.
- `references/cli.md` — load when running Biome or wiring CI: all commands + flags, the `--write`/`ci` semantics, and the v1→v2 CLI delta table.
- `references/gritql-plugins.md` — load when authoring a custom rule: plugin registration, GritQL pattern syntax, `register_diagnostic`, a complete example, and limitations.
- `references/migration-monorepo.md` — load when migrating from ESLint/Prettier or configuring a monorepo: the `migrate` commands + caveats and the `extends`/`root` monorepo model.
- `references/sources.md` — research provenance.

## Body budget

- `description` ≤ 1,024 chars; body ≤ ~500 lines / 5,000 tokens; heavy content in `references/`.
