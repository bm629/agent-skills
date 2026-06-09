# Lefthook — extended `lefthook.yml` reference

Load this when you need a `lefthook.yml` option or behavior the main SKILL.md doesn't cover. Current major version: **Lefthook 2.x**.

## Hook anatomy

A top-level key is a Git hook name (`pre-commit`, `pre-push`, `commit-msg`, `post-merge`, `prepare-commit-msg`, …). Under a hook you define work as **`commands:`** (a named map — the classic form) or **`jobs:`** (a list — the flexible v2 form). Hook-level options:

| Key | Meaning |
|---|---|
| `parallel: true` | Run the hook's commands/jobs concurrently. |
| `piped: true` | Run sequentially; abort on the first failure. |
| `follow: true` | Stream child output live. |
| `skip:` / `only:` | Run/skip the whole hook on conditions (see below). |
| `exclude_tags:` | Tags to exclude from this hook's run. |

## Command options (under `commands.<name>`)

| Option | Meaning |
|---|---|
| `run:` | **Mandatory.** Shell command, executed via `sh`. |
| `glob:` | File filter, e.g. `"*.{ts,tsx}"`. A **list** of globs is allowed (≥ 1.10.10). Matched against repo-root-relative paths. |
| `root:` | Working directory for the command (a subtree). Does **not** change glob matching. For pre-commit/pre-push/custom-`files` it also filters paths; if all are filtered out, the command is skipped. |
| `exclude:` | Regexp (or list) of paths to drop, combined with `glob`. |
| `files:` | A custom command whose output populates `{files}`. |
| `file_types:` | Filter by type (`text`, `binary`, `executable`, `symlink`, …). |
| `stage_fixed:` | After the command runs, `git add` the (filtered) files. **`pre-commit` only.** Uses `files` if set, else `{staged_files}`; applies `glob`/`exclude`. |
| `skip:` / `only:` | Conditions (see below). |
| `tags:` | Labels for selective run/exclude. |
| `priority:` | Integer ordering when not parallel. |
| `env:` | Environment variables for the command. |
| `interactive:` / `use_stdin:` | Attach the command to the terminal / pass stdin. |
| `fail_text:` | Message shown on failure. |

## File-template variables (in `run:`)

| Variable | Populated with |
|---|---|
| `{staged_files}` | Files staged for commit (at `pre-commit`). |
| `{push_files}` | Committed-but-unpushed files (at `pre-push`). |
| `{all_files}` | All git-tracked files. |
| `{files}` | Output of the command-level `files:` command. |
| `{cmd}` | The `run:` value itself (for wrapping, e.g. Docker). |
| `{0}`, `{1}`, `{2}`, … | The git-hook arguments (`{0}` = all joined). |
| `{lefthook_job_name}` | The current command/job/script name. |

If the substituted file list exceeds the OS command-line length limit, Lefthook splits it and runs the command sequentially over the chunks.

## `skip` / `only` conditions

A list of any of:

- `true` — always skip.
- `merge`, `rebase`, `merge-commit` — current Git state.
- `ref: main` — on a branch (glob refs like `ref: dev/*` are allowed).
- `run: <shell>` — skip when the shell command exits `0`.

`only:` is the inverse (run *only* when the condition holds). Both apply at hook level or command level.

## The `jobs:` form

`jobs:` is a list; each entry is either a leaf (`name` + `run`/`script`) or a **group** (`group:` with its own `parallel`/`piped` and nested `jobs:`). Named jobs are merged across `extends`/local config; unnamed jobs are appended in definition order. (`jobs:` was added in **Lefthook 1.10.0** — it is *not* a v2-only feature; it coexists with the classic `commands:`.) `glob`, `root`, and `exclude` set on a **group** apply to every nested job — handy for scoping a whole subtree's pipeline at once.

```yaml
pre-commit:
  parallel: true
  jobs:
    - name: migrate
      root: backend/
      glob: "db/migrations/*"
      group:
        piped: true
        jobs:
          - run: bundle install
          - run: rails db:migrate
    - name: lint-frontend
      root: frontend/
      run: yarn lint --fix {staged_files}
```

`commands:` and `jobs:` can't be mixed under the same hook — pick one. `commands:` is fine for simple per-language lanes; `jobs:` earns its keep when you need nested flow control.

## Global / top-level keys

| Key | Meaning |
|---|---|
| `min_version:` | Warn/fail if the installed Lefthook is older. Use it to pin the major version. |
| `assert_lefthook_installed:` | Fail the hook if Lefthook isn't installed (instead of silently passing). |
| `skip_output:` | Trim Lefthook's own output (e.g. `meta`, `success`, `skips`). |
| `source_dir:` / `source_dir_local:` | Where `scripts:` live (default `.lefthook/` and `.lefthook-local/`). |
| `colors:` | Toggle/override colored output. |
| `extends:` | Merge in other config files. |
| `lefthook:` | Override how the binary is located (e.g. a wrapper). |

A `lefthook-local.yml` (gitignored) lets a developer override or skip jobs locally without editing the shared config.

## Bypassing hooks

- `git commit --no-verify` / `git push --no-verify` (`-n`) — skip all Git hooks.
- `LEFTHOOK=0` or `LEFTHOOK=false` before a `git` command — disable Lefthook for that invocation.
- `LEFTHOOK_EXCLUDE=<tags/names>` — exclude specific tagged commands for one run (overrides `exclude_tags`).
- `CI=true` — the npm package's `postinstall` skips installing hooks (set in CI); `LEFTHOOK=1`/`true` forces it on.

## Version / migration notes

- Current major version is **2.x** (latest 2.1.9, May 2026; v2.0.0 succeeded 1.13.6); the Go module path is `github.com/evilmartians/lefthook/v2`.
- The flexible `jobs:` structure (with `group:` + nested `parallel`/`piped`) was **added in v1.10.0** — it is **not** a v2 feature; it coexists with the classic `commands:`. **v2.0.0**'s actual breaking changes were CLI-argument renames (see `lefthook run -h`) and switching the executor for `only`/`skip` `run:` conditions to Bourne shell, plus a refactor dropping some long-deprecated options.
- Very old configs may use `runner:` — the current key is `run:`. Author against the current schema; `min_version:` warns when a teammate's binary is too old.
- The npm `lefthook` package auto-installs hooks via its own `postinstall`. For `pnpm`, add `lefthook` to `pnpm.onlyBuiltDependencies` (and `pnpm-workspace.yaml`'s `onlyBuiltDependencies`) or that postinstall is skipped.
- Known issue: `lefthook install` can bake the install-time absolute path into the hook shim, which has broken **git worktrees** — re-run `lefthook install` inside a worktree if hooks misfire.
