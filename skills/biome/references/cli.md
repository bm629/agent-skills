# Biome CLI

Load when running Biome or wiring CI.

## Commands

| Command | Does |
|---|---|
| `biome check` | Runs formatter + linter + import sorting over the files. The all-in-one command. |
| `biome lint` | Lint only. |
| `biome format` | Format only. |
| `biome ci` | CI mode — runs format + lint + import-sort checks, **read-only (never writes)**. |
| `biome migrate` | Update config on breaking changes; `migrate eslint` / `migrate prettier` subcommands port other tools. |

## Fix flags

| Flag | Effect |
|---|---|
| `--write` | Apply **safe** fixes + formatting + import sorting. |
| `--write --unsafe` | Also apply **unsafe** fixes. (`--unsafe` is used with `--write`/`--fix`.) |
| `--fix` | Alias for `--write`. |

```sh
biome check --write .            # safe fixes
biome check --write --unsafe .   # + unsafe fixes
biome ci .                       # CI: check-only, no writes
```

## v1 → v2 CLI deltas (the stale-knowledge traps)

| v1 | v2 | Note |
|---|---|---|
| `biome check --apply` | `biome check --write` | `--apply` was removed; emitting it now errors. |
| `biome check --apply-unsafe` | `biome check --write --unsafe` | same change for unsafe fixes. |

Old training data and snippets frequently use `--apply` — always use `--write` for Biome v2.

## migrate

```sh
biome migrate eslint --write     # ports ESLint config (flat + legacy) and .eslintignore
biome migrate prettier --write   # ports Prettier config
```

Both need Node.js to resolve plugins/configs; see `migration-monorepo.md` for caveats.
