# `biome.json` configuration

Load when writing or adjusting the config. `biome init` scaffolds it; `$schema` gives editor validation.

## Top-level keys

| Key | Purpose |
|---|---|
| `$schema` | URL to the version-matched JSON schema (editor autocomplete/validation). |
| `extends` | Array of other config files to inherit from (monorepo / shared base). |
| `root` | Boolean (default `true`) — marks a root config; nested configs set `false` and `extends` the root. |
| `files` | `includes` glob list (with `!` negations), scan behavior. |
| `vcs` | Version-control integration. |
| `formatter` | Shared (all-language) formatter options. |
| `linter` | Lint enablement + rules. |
| `assist` | Code actions (incl. import organizing). |
| `javascript` / `json` / `css` / `graphql` / `grit` / `html` | Per-language overrides. |
| `overrides` | Per-glob config overrides. |
| `plugins` | GritQL plugin paths (see `gritql-plugins.md`). |

## formatter

```jsonc
"formatter": {
  "enabled": true,
  "indentStyle": "tab",      // "tab" (DEFAULT) | "space"
  "indentWidth": 2,
  "lineEnding": "lf",
  "lineWidth": 80,           // default 80
  "attributePosition": "auto",
  "bracketSpacing": true
}
```

Per-language formatting (e.g. JS quote style) goes under the language key, e.g. `"javascript": { "formatter": { "quoteStyle": "double" } }`.

## linter

```jsonc
"linter": {
  "enabled": true,
  "includes": ["src/**/*.js"],
  "rules": {
    "recommended": true,
    "correctness": "error",            // set a whole group
    "style": { "noVar": "error" },     // or individual rules
    "nursery": { "recommended": true }
  }
}
```

Rule groups: `accessibility`, `complexity`, `correctness`, `nursery`, `performance`, `security`, `style`, `suspicious`. Distinct from groups, Biome v2 **domains** (`linter.domains`, e.g. `react`, `test`, `next`, `project`) enable curated rule sets for a domain — e.g. `"domains": { "react": "recommended" }`. v2 also adds **type-aware** rules that work without the TypeScript compiler and **multi-file/project analysis** (rules that reason across files); confirm specifics against the current docs.

## assist (incl. import organizing)

In v2 import organizing is an **assist action**, not a top-level `organizeImports` (the v1 shape):

```jsonc
"assist": {
  "enabled": true,
  "actions": { "source": { "organizeImports": "on" } }
}
```

## vcs

```jsonc
"vcs": { "enabled": true, "clientKind": "git", "useIgnoreFile": true }
```

`useIgnoreFile: true` makes Biome respect `.gitignore` (recommended).

## overrides

```jsonc
"overrides": [
  { "includes": ["**/*.test.ts"], "linter": { "rules": { "suspicious": { "noExplicitAny": "off" } } } }
]
```

## v2 config-shape changes (vs v1)

- `organizeImports` (top-level, v1) → `assist.actions.source.organizeImports` (v2).
- `files.include` + `files.ignore` (v1) → single `files.includes` glob list with `!` negations (v2).
- See `cli.md` for the CLI deltas.
