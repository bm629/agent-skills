# Migrating from ESLint/Prettier + monorepo setup

## Migrate from ESLint / Prettier

```sh
biome migrate eslint --write     # reads ESLint config, ports settings to biome.json
biome migrate prettier --write   # reads Prettier config, ports settings
```

- **ESLint:** handles both legacy (`.eslintrc*`) and flat configs, processes `extends`, loads shared/plugin configs, and migrates `.eslintignore`. Needs Node.js to resolve plugins/configs. Does **not** support YAML-formatted ESLint config. Add `--include-inspired` to also migrate rule variations Biome was inspired by.
- **Prettier:** ports `.prettierrc`; Biome matches Prettier closely but uses different defaults (notably tabs vs spaces), so review the result. Does **not** support JSON5/TOML/YAML Prettier configs.
- Both recommend enabling Biome's VCS integration (`vcs.useIgnoreFile`) since ESLint/Prettier honored ignore files.

After migrating, remove ESLint/Prettier and their configs so you don't run two toolchains over the same files.

## Monorepo

Biome supports a root config plus nested configs:

- The repo-root `biome.json` is the **root** (`root: true`, the default).
- A package-level `biome.json` sets `root: false` and `extends` the root config (path to it), overriding only what it needs.

```jsonc
// packages/app/biome.json
{ "root": false, "extends": ["../../biome.json"], "linter": { "rules": { "style": { "noVar": "off" } } } }
```

## Running Biome in a Turborepo/pnpm pipeline

Define a `lint`/`format` (or `check`) task that runs `biome ci .` (CI) or `biome check --write .` (local), and let Turborepo cache + orchestrate it across packages. The pipeline wiring, caching, and task dependencies belong to the `turborepo` skill — this skill only provides the Biome command to run.
