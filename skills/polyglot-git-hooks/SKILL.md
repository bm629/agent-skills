---
name: polyglot-git-hooks
description: >
  Use when setting up Git hooks for a polyglot or monorepo project with
  Lefthook — wiring fast format/lint checks on staged files at pre-commit
  and slower type-check/test gates at pre-push, across mixed-language
  subtrees (e.g. TypeScript and Python) from a single lefthook.yml, in
  parallel. Covers install + activation, the lefthook.yml schema
  (commands/jobs, glob, root, run with {staged_files}/{push_files},
  stage_fixed, skip/only, parallel), a genuinely polyglot worked example,
  the hooks-vs-CI division of labor, and the --no-verify bypass. Teaches
  the hook wiring; references the per-tool skills (biome, ruff, ty,
  typescript-typecheck) and turborepo rather than re-teaching them. Keywords:
  git hooks, pre-commit, pre-push, lefthook, staged files, monorepo hooks,
  polyglot lint format.

extensions:
  claude:
    when_to_use: "Setting up or editing Git hooks (pre-commit/pre-push) for a polyglot/monorepo with Lefthook."
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

# `polyglot-git-hooks` — SKILL.md

> **Variant:** standard · **When to use:** the skill is invoked, you produce a `lefthook.yml` and wire it, control returns to the caller. The tool taught is **Lefthook** (a Git-hooks manager); the skill is named for its differentiator — driving checks across *multiple languages* from one config.

## Overview

This skill sets up **Git hooks for a polyglot repo with Lefthook** — a fast, Go-based, language-agnostic hooks manager. The goal is one `lefthook.yml` at the repo root that runs the *right fast checks on staged files* at `pre-commit` (format + lint) and the *slower checks* at `pre-push` (type-check + tests), across a mixed-language repo (e.g. a TypeScript subtree and a Python subtree), in parallel. It is the local "fail fast before the commit/push" layer that **complements, not replaces, CI**. This skill owns the **hook wiring** — the per-tool details (how Biome/Ruff/tsc/ty themselves work) belong to their own skills, which this one references.

## When to activate

- ✅ Setting up Git hooks for a repo (a new `lefthook.yml`), or adding a `pre-commit` / `pre-push` gate.
- ✅ Wiring lint/format/type-check to run on **staged files** before a commit, or on push files before a push.
- ✅ Configuring hooks for a **polyglot or monorepo** where different subtrees use different toolchains.
- ✅ Migrating off husky+lint-staged or the Python `pre-commit` framework to a single-config, polyglot setup.

**Do NOT activate when:**

- You need to learn or configure a specific linter/formatter/type-checker itself — use that tool's skill (`biome`, `ruff`, `ty`, `typescript-typecheck`).
- You are designing the **CI pipeline** (full, authoritative checks on the server) — hooks are the *local* gate; CI is separate (see Step 5 and the `turborepo` skill).
- The task is enforcing a `--no-verify` ban as org policy — that is a narrow policy-hook concern, not hook *setup* (see Gotchas).

## Workflow

### Step 1: Pick Lefthook, know why

Lefthook is a single dependency-free binary (written in Go) that manages Git hooks for any language. Choose it over the alternatives for a polyglot repo because:

- **vs husky + lint-staged** — husky is JS/Node-only and needs `lint-staged` bolted on for staged-file filtering; the config ends up split across `.husky/pre-commit`, a `lint-staged` key in `package.json`, and `package.json` scripts, and pulls a large dependency tree into `node_modules`. Lefthook is **one `lefthook.yml`, one binary, native staged-file filtering**, no extra runtime deps. In a mixed frontend/backend team, husky+lint-staged tends to mean two separate setups.
- **vs the Python `pre-commit` framework** — `pre-commit` is Python-centric (it manages its own per-hook tool environments) and is weaker for TS/mixed repos. Lefthook runs commands **in parallel**, is a single compiled binary instead of a Python script, and works equally across languages and large monorepos. (`pre-commit` still has a broader catalog of ready-made hooks and is simpler for small/Python-only projects — a fair trade to acknowledge, not the choice here.)

### Step 2: Install + activate

Install Lefthook as a dev dependency or a binary, then wire it into `.git/hooks` with `lefthook install`.

- **npm:** `npm install lefthook --save-dev` (also published as `@evilmartians/lefthook`). The `lefthook` npm package runs its own `postinstall` that calls `lefthook install`, so **a fresh `npm install` wires the hooks automatically** — the fresh-clone activation problem is solved for npm users out of the box. (See the fresh-clone note below.)
- **Binary / non-npm:** install via Homebrew, `go install`, `pipx install lefthook`, `gem install lefthook`, apt, snap, or winget, then run `lefthook install` once.

Put a single `lefthook.yml` at the **repo root**. Verify the wiring with `lefthook install` (idempotent — safe to re-run).

**Fresh-clone activation (load-bearing).** Hooks live in each developer's local `.git/hooks`, which is **not** committed — so a teammate who just cloned the repo has *no* hooks until something runs `lefthook install`. Two ways to make a clone self-wire:

- **npm projects:** rely on the `lefthook` package's `postinstall` (automatic on `npm install`), or add an explicit `"prepare": "lefthook install"` script to `package.json` so it runs after install. (For `pnpm`, add `lefthook` to `pnpm.onlyBuiltDependencies` / `pnpm-workspace.yaml`'s `onlyBuiltDependencies`, or the postinstall is skipped and hooks never wire.)
- **Non-npm projects:** document `lefthook install` as a required setup step in the README, or run it from a bootstrap/setup script.

In CI you usually do **not** want the hooks installed by the postinstall — set `CI=true` (most CI sets it already) to skip it; use `LEFTHOOK=1` to force it on when needed.

### Step 3: Author the `lefthook.yml` schema

Top-level keys are **Git hook names** — `pre-commit`, `pre-push` (any hook name works: `commit-msg`, `post-merge`, …). Under each hook, define work as either:

- **`commands:`** — a map of named commands (the classic form), or
- **`jobs:`** — a list of jobs (the flexible form; supports commands, scripts, and nested groups with their own `parallel`/`piped` flow). `glob`/`root`/`exclude` set on a group apply to all nested jobs.

Use whichever reads cleaner; the examples here use `commands:`. Hook-level and command-level options you will reach for:

| Option | Where | What it does |
|---|---|---|
| `run:` | command | The shell command (runs via `sh`). **Mandatory.** |
| `glob:` | command | Filter to matching files, e.g. `"*.{ts,tsx}"`. A **list** of globs is allowed (Lefthook ≥ 1.10.10). If a file template is omitted from `run`, Lefthook still filters `{staged_files}` (pre-commit) / `{push_files}` (pre-push) by the glob and **skips the command when nothing matches**. |
| `root:` | command | Change the command's working directory to a subtree (e.g. `apps/web/`). Useful when a `package.json`/config lives in a subdir. **Globs are still computed from the git repo root — `root` does not change glob matching** — but the file paths Lefthook substitutes into `{staged_files}` for the command are rebased to be relative to `root`, so the tool receives subtree-relative paths. |
| `exclude:` | command | Drop files matching a regexp (or list), combined with `glob`. |
| `stage_fixed:` | command | After the command runs, `git add` the (filtered) files so auto-fixes are re-staged. **Works only for `pre-commit`.** |
| `parallel:` | hook | `true` → run the hook's commands concurrently. |
| `piped:` | hook/group | `true` → run sequentially, stopping on the first failure. |
| `skip:` / `only:` | hook or command | Conditions: `true` (always), `merge` / `rebase` / `merge-commit`, `ref: main` (glob refs like `ref: dev/*`), or `run: <shell>` (skip if the command exits 0). |
| `tags:` / `priority:` | command | Group/order commands. |

**File-template variables** for `run:` — substituted at execution:

- `{staged_files}` — files staged for the commit (populated at `pre-commit`).
- `{push_files}` — committed-but-unpushed files (populated at `pre-push`).
- `{all_files}` — all git-tracked files.
- `{files}` — the result of a custom `files:` command.
- `{cmd}` — the command from `lefthook.yml` (for wrapping, e.g. in Docker).

If a file list is too long for the OS command-line limit, Lefthook splits it and runs the command sequentially over the chunks.

### Step 4: The polyglot worked example

A complete root `lefthook.yml` for a repo with a **TypeScript subtree** and a **Python subtree**. `pre-commit` runs fast, auto-fixing, staged-file checks **in parallel**, each scoped to its language; `pre-push` runs the slower type-check + test gates before code leaves the machine.

```yaml
# lefthook.yml — at the repo root
min_version: 2.0.0          # pin the major version; warn on older Lefthook

pre-commit:
  parallel: true
  commands:
    # --- TypeScript / JavaScript: format + lint staged files, re-stage fixes ---
    biome:
      glob: "*.{js,jsx,ts,tsx}"
      run: biome check --write {staged_files}
      stage_fixed: true

    # --- Python: lint-fix + format staged files in the python subtree ---
    ruff:
      root: "services/api/"          # CWD for the command (a python subtree)
      glob: "*.py"                   # computed from the repo root, not from `root`
      run: ruff check --fix {staged_files} && ruff format {staged_files}
      stage_fixed: true

pre-push:
  parallel: true
  commands:
    # --- TypeScript: whole-project type-check (no file template; checks the project) ---
    tsc:
      glob: "*.{ts,tsx}"
      run: tsc --noEmit

    # --- Python: type-check the subtree ---
    ty:
      root: "services/api/"
      glob: "*.py"
      run: ty check

    # --- Tests: run the suites (heavier; pre-push, not pre-commit) ---
    test-ts:
      glob: "*.{ts,tsx}"
      run: npm test

    test-py:
      root: "services/api/"
      glob: "*.py"
      run: pytest
```

Why this shape:

- **`pre-commit` = fast + staged-only.** `biome check --write` and `ruff check --fix` / `ruff format` only touch `{staged_files}`, so the hook is fast and edits only what you are committing. `stage_fixed: true` re-stages the auto-fixes so the commit includes the formatted result (and `stage_fixed` is valid only here, at `pre-commit`).
- **Scope per subtree.** Each command is bounded by `glob` (language) and, for the Python side, `root` (the subtree's directory) so the right tool runs on the right files. Remember `glob` matches against repo-root-relative paths even when `root` is set.
- **`pre-push` = slow + thorough.** Type-checking (`tsc --noEmit`, `ty check`) and tests are project-wide and too slow to run on every commit, so they gate the **push** instead. Here the glob just decides *whether* the command runs (skip if no files of that language changed); the type-checkers and test runners then check the project, not just the changed files. `{push_files}` is available if you want to scope a push-time command to the changed set.
- **Parallel.** `parallel: true` runs the language lanes concurrently — the TS and Python checks don't wait on each other.

The per-tool invocations (`biome check`, `ruff check`/`ruff format`, `tsc --noEmit`, `ty check`) are owned by their own skills — see `## Related`. This file owns only the **wiring**.

### Step 5: Place hooks against CI (don't duplicate)

Hooks and CI are **different layers** — wire them as a division of labor, not a copy:

- **Hooks = local, staged, fast.** They catch the obvious before the commit/push leaves your machine: formatting, lint, a quick type-check/test gate at push. Speed matters because they run on every commit; keep `pre-commit` to staged-file fast checks and push the slow stuff to `pre-push`.
- **CI = full, authoritative.** CI runs the complete suite on the server over the whole repo and is the *enforced* gate (a merge requirement) — because hooks are local and **bypassable** (Step 6), CI is what actually guarantees the checks ran.

Do **not** restate the CI pipeline inside `lefthook.yml`. Where a repo uses a task runner, a hook command may *call* a task (e.g. `turbo run lint`) rather than re-listing pipeline steps — but the pipeline definition itself lives with the task runner, not in the hook config. See the `turborepo` skill for the task graph; this skill does not duplicate it.

**No-CI-yet caveat (important).** When a repo has **no CI pipeline yet**, the hooks are the *primary* automated gate — there is no server-side net behind them. In that situation, **raise the bar on `pre-push`**: run the full type-check and test suites at push so nothing unverified leaves the machine, and treat the hook set as load-bearing until CI lands. Once CI exists, you can relax `pre-push` back toward a fast smoke gate and let CI own the exhaustive run.

### Step 6: Document the `--no-verify` bypass

Hooks are local and **can be skipped** — make sure the team knows when that is legitimate and that it is not a silent gap:

- `git commit --no-verify` (`-n`) and `git push --no-verify` skip Git hooks entirely.
- `LEFTHOOK=0` (or `LEFTHOOK=false`) before a `git` command disables Lefthook for that one invocation; `LEFTHOOK_EXCLUDE` overrides the `exclude_tags` config to drop specific tags/commands.

Legitimate uses: committing a known-incomplete WIP to a personal branch, or an emergency hotfix where the hook is blocking and CI will re-check anyway. Because the bypass exists, **CI — not the hook — is the enforced gate** (Step 5). Some teams add a **policy hook that blocks `--no-verify`** to make the bypass deliberate; a published example is `wshobson/agents@block-no-verify-hook`. That is a separate enforcement concern — named here as a pointer, not set up by this skill.

## Rules

**Hard rules (never violate):**

- **One `lefthook.yml` at the repo root.** A single language-agnostic config is the whole point; don't fragment it per language.
- **`pre-commit` is fast + staged-only.** Run format/lint on `{staged_files}` with `stage_fixed: true`; never put whole-repo type-checks or full test suites at `pre-commit`.
- **`pre-push` carries the slow gates.** Type-check and tests go here, not at `pre-commit`.
- **Scope every command.** Bound each command with `glob` (and `root` for a subtree) so the right tool runs on the right files. Don't run a Python tool over TS files or vice-versa.
- **This skill owns wiring, not tools.** Reference `biome`/`ruff`/`ty`/`typescript-typecheck` for tool flags; reference `turborepo` for the CI/task graph. Do not re-teach or duplicate them.
- **Pin the major version** with `min_version:` (current major: **Lefthook 2.x**) so a teammate on an older binary is warned rather than silently misbehaving.

**Preferences (override-able):**

- Prefer `commands:` for simple per-language lanes; reach for `jobs:` + groups when you need nested `piped`/`parallel` flow control.
- Use `parallel: true` to run independent language lanes concurrently.
- Add `skip: [merge, rebase]` to commands that shouldn't run mid-merge/rebase.

## Gotchas

- **Fresh clone, no hooks.** Hooks live in `.git/hooks`, which is not committed — a teammate who clones gets nothing until `lefthook install` runs. Symptom: "the hook never ran for them." Fix: rely on the npm `postinstall` (npm projects) or add a `prepare` script / document `lefthook install` (Step 2). For `pnpm`, the postinstall is skipped unless `lefthook` is in `onlyBuiltDependencies`.
- **`root` does not move glob matching.** Setting `root: "services/api/"` changes the command's CWD but `glob` patterns are still evaluated against **repo-root-relative** paths. A glob like `"services/api/**/*.py"` (full path) or a plain `"*.py"` (matches any depth) works; do not write the glob as if it were relative to `root`.
- **`stage_fixed` is `pre-commit`-only.** It is ignored at `pre-push` and other hooks. If a formatter's fixes aren't being committed, confirm the command is under `pre-commit` and that `stage_fixed: true` is set on *that* command.
- **Empty match = skipped command (usually what you want).** With a `glob` and no matching staged files, Lefthook skips the command rather than running it on zero files — so a TS-only commit won't trigger the Python lane. Don't add manual "if no files" guards; the glob already does it.
- **Stale config keys from old versions.** Lefthook 2.x is current; very old configs/blog posts may use a deprecated key (e.g. `runner:` instead of `run:`). Author against the current schema and let `min_version:` flag a too-old binary. The Go module path is also `.../lefthook/v2` for v2.
- **`lefthook install` and worktrees.** `lefthook install` can bake the install-time absolute path into the hook shim, which has been known to break **git worktrees** — re-run `lefthook install` in the worktree if hooks misfire there.
- **Hooks are not enforcement.** Anyone can `--no-verify`. Treat hooks as a fast local convenience and let **CI** be the gate that actually blocks a merge (Step 5/6).

## Anti-patterns

- **"Put the full test suite at `pre-commit` so nothing slips."** No — that makes every commit slow and trains the team to `--no-verify`. Fast staged checks at `pre-commit`; slow gates at `pre-push`; exhaustive runs in CI.
- **"Just lint the whole repo each commit."** No — use `{staged_files}` so the hook touches only what's being committed; whole-repo runs belong to CI.
- **"Copy the CI pipeline steps into `lefthook.yml` so they match."** No — that duplicates and drifts. Reference the task runner (`turborepo`) and keep the pipeline definition in one place.
- **"Skip `glob`/`root` — one command for everything."** No — an unscoped command runs the wrong tool on the wrong files in a polyglot repo. Scope per language/subtree.
- **"Skip `lefthook install` in the setup docs; people will figure it out."** No — that's the #1 reason hooks silently don't run for new contributors. Make activation automatic or documented.

## Output

This skill produces a single **`lefthook.yml`** at the repo root, plus the activation wiring (a `prepare`/`postinstall` hook for npm projects or a documented `lefthook install` step), configured for a polyglot repo: a `pre-commit` running format/lint on staged files per language with `stage_fixed`, and a `pre-push` running the type-check + test gates. The artifact's consumer is every contributor's local Git (the hooks fire on commit/push) and, by extension, the reviewer/CI layer that the hooks pre-empt. The per-tool commands and the CI pipeline are referenced, not embedded.

## Related

- `biome` — TS/JS format + lint; supplies the `biome check --write` invocation used in the `pre-commit` example.
- `ruff` — Python lint + format; supplies the `ruff check --fix` / `ruff format` invocations.
- `ty` — Python type-checker; the `pre-push` Python gate.
- `typescript-typecheck` — the `tsc --noEmit` type-check gate for the `pre-push` TS lane.
- `turborepo` — the monorepo task graph / CI pipeline; a hook may *call* a turbo task, but the pipeline lives there, not in `lefthook.yml`.
- `references/lefthook-reference.md` — fuller `lefthook.yml` schema notes, the `jobs:` form, and version/migration details. Load when you need an option this SKILL.md doesn't cover.
- `references/sources.md` — research provenance.

## Progressive disclosure

- `references/lefthook-reference.md` — extended schema reference (full option list, the `jobs:`/groups form, global keys, version notes). **Load trigger:** you need a `lefthook.yml` option or behavior not covered in the Workflow above.
- `references/sources.md` — citations for the facts in this skill. **Load trigger:** verifying or updating a claim.

No `scripts/` or `assets/` ship with this skill — it produces a `lefthook.yml` you author from the examples above, not a generator.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap).
- Body ≤ ~500 lines / 5,000 tokens — kept in context every turn.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k tokens, error >50k.
