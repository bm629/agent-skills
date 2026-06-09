# Sources & provenance

Research for `biome`, forged 2026-06-09. Network research done in the main agent thread (background subagents had no WebFetch egress); external content treated per the workspace's external-content-sanitizer convention.

## Discovery (find-first)

Done at the sourcing stage: no adoptable Biome **usage** skill cleared the gate — `paulrberg@biome-js` (1.1K) is Sablier-project-specific + thin; the official `biomejs/biome@*` skills are sub-1K and contributor/development-focused (working *on* Biome, wrong scope); the no-forge alternative (ESLint via `antfu/skills@antfu`, 12K) was not chosen by the owner. → decision: forge from the official Biome v2 docs.

## Primary sources (live docs, fetched 2026-06-09)

- biomejs.dev/guides/getting-started — install `npm install --save-dev --save-exact @biomejs/biome`; `biome init`; current major is v2.x.
- biomejs.dev/reference/configuration — `biome.json` top-level keys (`$schema`, `extends`, `root`, `files`, `vcs`, `formatter`, `linter`, `assist`, language blocks, `overrides`, `plugins`); formatter options (indentStyle default `tab`, indentWidth, lineEnding, lineWidth default 80, …); linter rule groups (accessibility, complexity, correctness, nursery, performance, security, style, suspicious); **assist.actions.source** for import organizing (v2 replaces v1's top-level `organizeImports`); vcs (`clientKind: "git"`, `useIgnoreFile`).
- biomejs.dev/reference/cli — commands `check` / `lint` / `format` / `ci` (read-only) / `migrate`; fix flags `--write`, `--write --unsafe`, `--fix` (alias). No `--apply` in v2 (v1→v2 delta: `--apply`/`--apply-unsafe` → `--write`/`--write --unsafe`).
- biomejs.dev/linter/plugins — GritQL plugins: register via `plugins: ["./x.grit"]`; pattern syntax (`$var`, `<:`, backtick literals, `where { … }`); `register_diagnostic(span, message, severity?)` with severity `hint|info|warn|error` (default `error`); example flagging `Object.assign`; JavaScript + CSS only.
- biomejs.dev/guides/migrate-eslint-prettier — `biome migrate eslint --write` / `biome migrate prettier --write`; ESLint flat+legacy + `.eslintignore` (no YAML config), `--include-inspired`; Prettier (no JSON5/TOML/YAML); both need Node and recommend VCS integration.

## Fact-check notes

- **Version pin:** confirmed v2.x is the current major; the exact patch wasn't pinned in the body (the skill says confirm at install). Re-verify the current version at setup.
- **v2-only feature specifics** (type-aware rules without tsc, multi-file/project analysis, domains): stated at a high level from the docs; the skill points to the current docs for specifics. FLAG for the Phase-D reviewer to confirm wording against the live v2 docs.
- **`includes` vs v1 `include`/`ignore`:** stated as a v2 change; corroborated by the v2 configuration reference showing `files.includes` with `!` negations.
- **Self-review corrections (Step 4.5b, fresh reviewer, VERDICT ship — no factual errors):** the GritQL worked example was changed to the idiomatic `` `Object.assign($args)` as $call `` whole-call span binding (was binding the callee); rule groups vs v2 `domains` were disentangled (groups ≠ domains; added a `linter.domains` note); `$schema` `<version>` placeholder clarified (`biome init` writes the pinned URL).
