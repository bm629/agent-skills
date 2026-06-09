# Sources — polyglot-git-hooks

Research provenance for the `polyglot-git-hooks` skill (Lefthook). Gathered 2026-06-09 from the live official Lefthook documentation, the `evilmartians/lefthook` GitHub repo, and the project's official wiki. All external content was passed through `external-content-sanitizer` before use (clean — no injection). Facts are paraphrased; no source text copied verbatim.

## Version pin

- **Lefthook 2.x** is the current major version (latest at research time: **v2.1.9**, May 2026). The Go module path is `github.com/evilmartians/lefthook/v2`. v2 added the flexible `jobs:` form alongside the classic `commands:`.
  - GitHub repo + Releases: `github.com/evilmartians/lefthook`, `github.com/evilmartians/lefthook/releases`
  - PyPI version history: `pypi.org/project/lefthook`

## What Lefthook is / why over alternatives

- Project description, "fast (Go, parallel) / powerful / simple (single dependency-free binary)": `github.com/evilmartians/lefthook` (README).
- Comparison vs husky+lint-staged (split config across `.husky/pre-commit` + `lint-staged` key + scripts; ~1500 node_modules deps; two setups in mixed teams) and vs the Python `pre-commit` framework (parallel, single binary vs Python script, monorepo/polyglot strength; pre-commit has broader ready-made hook catalog, simpler for small/Python-only):
  - Official wiki "Comparison with other solutions": `github.com/evilmartians/lefthook/wiki/Comparison-with-other-solutions`
  - Evil Martians blog "Lefthook: knock your team's code back into shape": `evilmartians.com/chronicles/lefthook-knock-your-teams-code-back-into-shape`
  - Husky-migration wiki: `github.com/evilmartians/lefthook/wiki/Migration-from-husky-with-lint-staged`

## Install + activation

- Install methods (npm `lefthook` / `@evilmartians/lefthook` / `@evilmartians/lefthook-installer`, `go install .../v2`, `gem install lefthook`, `pipx install lefthook`, Homebrew/apt/snap/winget), `lefthook install` wiring, npm `postinstall` auto-install, `CI=true` to skip / `LEFTHOOK=1` to force, pnpm `onlyBuiltDependencies`:
  - Install docs: `lefthook.dev/install/`, `lefthook.dev/installation/node/`, `lefthook.dev/installation/index.html`
  - README install section: `github.com/evilmartians/lefthook`
  - npm package: `npmjs.com/package/lefthook`, `npmjs.com/package/@evilmartians/lefthook`

## lefthook.yml schema

- `commands:` options (run, glob, files, file_types, env, root, exclude, fail_text, stage_fixed, interactive, use_stdin, priority, skip, only, tags): `lefthook.dev/configuration/Commands/`
- `run:` + file-template variables (`{staged_files}`, `{push_files}`, `{all_files}`, `{files}`, `{cmd}`, `{0}/{1}`, `{lefthook_job_name}`) + command-line-length splitting: `lefthook.dev/configuration/run/`
- `glob:` (list of globs since v1.10.10; skip-on-no-match; checks `{staged_files}` at pre-commit / `{push_files}` at pre-push): `lefthook.dev/configuration/glob/`
- `root:` (changes CWD; globs still computed from repo root; filters paths, skip-if-all-filtered): `lefthook.dev/configuration/root/`
- `stage_fixed:` (re-stage via `git add`; pre-commit only; applies glob/exclude; uses `files` or `{staged_files}`): `lefthook.dev/configuration/stage_fixed/`, example `lefthook.dev/examples/stage_fixed/`
- `exclude:`: `lefthook.dev/configuration/exclude/`
- `skip:` / `only:` (true / merge / rebase / merge-commit / `ref:` glob / `run:` shell): `lefthook.dev/configuration/skip/`
- `jobs:` (name/run/group; groups parallel/piped; glob/root/exclude on a group apply to nested jobs; named merged, unnamed appended): `lefthook.dev/configuration/jobs/`
- Global keys (`min_version`, `assert_lefthook_installed`, `skip_output`, `source_dir`): `lefthook.dev/configuration/`, `lefthook.dev/configuration/lefthook/`

## Bypass

- `git commit/push --no-verify` skips hooks (standard Git). `LEFTHOOK=0`/`false` disables Lefthook per invocation; `LEFTHOOK_EXCLUDE` overrides `exclude_tags`: `lefthook.dev/usage/envs/LEFTHOOK.html`, `lefthook.dev/usage/envs/CI.html`
- Policy hook that blocks `--no-verify` (named as a pointer, not adopted): `wshobson/agents@block-no-verify-hook`.

## Known issue

- `lefthook install` baking an install-time absolute path into the hook shim, breaking git worktrees: `github.com/evilmartians/lefthook` issue #1398.

## Notes on degraded research steps

- The live `npx skills find` discovery re-sweep and direct `WebFetch` of `lefthook.dev` pages were blocked by the execution sandbox; the sourcing decision (FORGE — no adoptable skill) is carried from the approved skill spec, and `lefthook.dev` content was instead gathered via `WebSearch` summaries of the official doc pages plus `WebFetch` of the GitHub raw docs/README (which were permitted). All facts were cross-checked across ≥2 official sources before synthesis.
