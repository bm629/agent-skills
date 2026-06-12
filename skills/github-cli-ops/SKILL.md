---
# ─── UNIVERSAL CORE ──────────────────────────────────────────────────────
name: github-cli-ops
description: >
  Use when performing a GitHub operation programmatically — creating an
  issue or pull request, managing repos, releases, labels, Actions runs,
  Projects, secrets, or any github.com task — preferring the `gh` CLI and
  falling back to `gh api` (REST) or `gh api graphql` only where no command
  exists. Every call is authenticated per-invocation with `GH_TOKEN`; it
  never runs `gh auth switch` and never prints the token. Uses `gh`'s
  high-level commands (which also encrypt secrets client-side) for coverage
  and ergonomics; for the REST long tail it builds a `gh api` call from a
  bundled OpenAPI spec via an endpoint index + a `$ref`-resolver. github.com
  Cloud; consumes caller-injected credentials (host + a token resolved by
  variable name) — it does not provision or resolve them.

# ─── PROVIDER-SPECIFIC EXTENSIONS ────────────────────────────────────────
extensions:
  claude:
    allowed-tools: [Read, Write, Edit, Grep, Glob, Bash]
    user-invocable: true
    when_to_use: "performing a GitHub operation via gh (CLI-first) or gh api"
    argument-hint: "<operation, e.g. 'create an issue'>"
  copilot: {}
  cursor:
    alwaysApply: false
    globs: []
  gemini: {}
  codex: {}

version: "1.0.0"

forge:
  status: reviewed
  forged: 2026-05-31
  reviewed: 2026-06-12
---

# github-cli-ops

## Overview

This skill lets an agent perform **any** GitHub operation, **CLI-first**: it uses the `gh` CLI for everything `gh` covers — the ergonomic path that also encrypts secrets and shapes output — and falls back to **`gh api`** (REST) only where no `gh` command exists, with **`gh api graphql`** for the GraphQL-only corners. Authentication is **per-call**: every invocation is prefixed with `GH_TOKEN="$<token var>"` from the caller-injected token, so nothing global is ever mutated. `gh` already manages base URL, pagination, and output, so the agent does not reimplement HTTP plumbing. For the REST long tail, the agent looks up an endpoint in a bundled OpenAPI spec via an **endpoint index + a `$ref`-resolver**, then constructs the `gh api` call.

## When to activate

- ✅ Performing a GitHub operation that has a first-class command — issues, pull requests, repos, releases, labels, gists, Actions runs/workflows, Projects, secrets, etc. (`gh <command>`).
- ✅ A REST operation with **no** first-class command — construct it via `gh api <endpoint>`.
- ✅ A GraphQL-only need (e.g. Discussions) — `gh api graphql`.
- ✅ A write you need done programmatically against github.com.

**Do NOT activate when:**

- The task is a **local/interactive** `gh` action — `gh auth …`, `gh browse`, `gh repo clone`, `gh pr checkout`, `gh config`, `gh alias`, `gh extension`, `gh completion`. Those are local conveniences, not API operations; use `gh`/`git` directly.
- The target is **GitHub Enterprise Server** as a first-class need (this skill is github.com in v1; an Enterprise host routes via the injected `host` + `GH_HOST`/`GH_ENTERPRISE_TOKEN` but is untested here).
- You only need credential setup — credentials are provided by the caller; this skill does not provision or resolve them (see [`references/auth.md`](references/auth.md) for the contract it consumes).

## Workflow

### Step 1 — Receive the injected credentials

The caller has already resolved the account and injected what this operation needs — **consume** it; do **not** look for a record yourself. You receive from context:

- **`host`** (and the **capability** the account acts under) — as context values, not read from a file.
- **The token, by an ordered load rule** the context carries the **variable NAME** for. Resolve that name as: the project-level **`.env` value if that file exists** and defines the var, **else** the **environment variable** of that name — project `.env` is tried first (that is how a project `.env` overrides a global env var). The token **value** is never in the context prose — only its variable name (`$<token_env>` in the examples below); only the `gh` subprocess reads it. The project root is supplied by the context; perform **no** scope resolution or directory walk to find the `.env`, and it is project `.env`, not `.envrc`.

Confirm the token works before real operations: `GH_TOKEN="$<token_env>" gh api user --jq .login`. **Never use `gh auth switch`/`gh auth login`** to select the account — they mutate `gh`'s global active account (shared across the user's shells); auth is **per-call** via `GH_TOKEN`. Full contract + the env bridge: [`references/auth.md`](references/auth.md).

### Step 2 — Decide CLI vs API

Scan [`assets/cli-index.md`](assets/cli-index.md) (one line per command) for a `gh` command that matches the operation. **Decision rule:** prefer a `gh` command whenever one exists; use `gh api` only for the gap; `gh api graphql` for GraphQL-only needs. Note: whole areas have **no** command (`teams`, `checks`, `packages`, `code-scanning`/`-security`, `dependabot`, `git` data, `reactions`, `apps`, `migrations`, …) — for those, skip the scan and go straight to `gh api` (the list is in [`references/gh-api.md`](references/gh-api.md)).

### Step 3a — CLI path (preferred)

Read the command's exact flags from live `gh <cmd> --help` (always current with the installed `gh`). Run it with the per-call token:

```bash
GH_TOKEN="$<token_env>" gh issue create --repo OWNER/REPO --title "…" --body "…"
GH_TOKEN="$<token_env>" gh repo view OWNER/REPO --json name,visibility,defaultBranchRef --jq '.defaultBranchRef.name'
GH_TOKEN="$<token_env>" gh secret set MYSECRET --repo OWNER/REPO --body "$VALUE"   # gh encrypts client-side
```

Use `--json <fields> [--jq <expr>]` for machine-readable output. See [`references/cli-reference.md`](references/cli-reference.md).

### Step 3b — API fallback

When no command exists: scan [`assets/endpoint-index.md`](assets/endpoint-index.md) for the operation, resolve its shape with `python3 scripts/endpoint.py <operationId>` (`$ref`-resolved params / body / response + a skeleton), then construct:

```bash
GH_TOKEN="$<token_env>" gh api repos/{owner}/{repo}/traffic/views --jq '.count'
GH_TOKEN="$<token_env>" gh api -X PATCH repos/{owner}/{repo} -f description='…'
GH_TOKEN="$<token_env>" gh api graphql -f query='{ viewer { login } }'
```

`{owner}`/`{repo}`/`{branch}` placeholders fill from the current repo or `GH_REPO`. Flags + pagination + GraphQL detail: [`references/gh-api.md`](references/gh-api.md).

### Step 4 — Handle the response

- **Output:** `--jq`/`--json` (CLI) or `--jq`/`--template` (`gh api`).
- **Pagination (`gh api`):** `--paginate` auto-follows `Link` headers; `--slurp` wraps all pages into one array. GraphQL paginate needs `$endCursor` + `pageInfo{hasNextPage,endCursor}` in the query.
- **Errors:** a non-zero exit / HTTP 4xx is the API's answer — most often a **token-scope** issue. Mint a token with the needed scopes (see [`references/auth.md`](references/auth.md)); it is not a skill bug.

## Rules

**Hard rules (never violate):**

- **Per-call `GH_TOKEN` only.** Authenticate every call with `GH_TOKEN="$<token_env>" gh …`. **Never** `gh auth switch`/`gh auth login` (they mutate global state). `GH_HOST`/`GH_ENTERPRISE_TOKEN` for non-default hosts.
- **Never read or print the token value.** Reference it only as `$<token_env>`; the `gh` subprocess reads it from the environment. The token lives only in `.env` (gitignored).
- **CLI-first.** Prefer a `gh` command when one exists; `gh api` is the gap-filler, `gh api graphql` for GraphQL-only. Do not hand-build a `gh api` call for something `gh` does natively.
- **Resolve before constructing a `gh api` call.** Build params/body from the `$ref`-resolved schema (Step 3b), not from a guessed/remembered field set.
- **Secrets via `gh secret set`.** It encrypts client-side; never hand-roll libsodium or PUT a raw secret value yourself.
- **This skill never writes credentials.** Credentials are provided by the caller; this skill never provisions or resolves them.

**Preferences (override-able):**

- Request only needed fields (`--json <fields>` on commands; `--jq`/`-q` to slice) to keep output small.
- Prefer a first-class command's structured output (`--json`) over scraping human text.
- For large `gh api` collections, use `--paginate` (and `--slurp` when you need a single combined array).

## Gotchas

- **`gh auth switch` is global.** It changes the active account for every shell, not just this call — the exact failure this skill avoids. Always pass `GH_TOKEN` per-invocation instead.
- **`-f` vs `-F` in `gh api`.** `-f/--raw-field` sends a **string**; `-F/--field` does magic typing (`true`/`false`/`null`/ints become JSON types, `@file` reads a file, `{owner}` placeholders fill). Using `-f` for a boolean/int sends the literal string and the API rejects it.
- **Adding fields flips the method to POST.** Any `-f`/`-F` switches `gh api` from GET to POST automatically; for a GET with query params use `-X GET` (or they go in the query string).
- **Token scope, not a bug.** A 4xx on a valid call is usually a missing token scope (e.g. `repo`, `delete_repo`, `read:org`). Surface it and mint a properly-scoped token; don't retry blindly.
- **Placeholders need a repo context.** `{owner}`/`{repo}` only fill from the current git repo or `GH_REPO`; outside a repo, pass the full path (`repos/OWNER/REPO/…`).
- **`gh auth status` with `GH_TOKEN` set** reports the env token and disables `login`/`switch` — expected; it means per-call auth is in effect.

## Anti-patterns

- **`gh auth switch` to pick an account.** Never — it mutates global state. Per-call `GH_TOKEN` is the only account selector here.
- **Echoing the token.** Never `echo $TOKEN`, never paste it into a printed command, never write its value into any file. Reference the env var only.
- **`gh api` for what `gh` does natively.** Don't hand-build `gh api repos/{owner}/{repo}/issues -f title=…` when `gh issue create` exists — you lose ergonomics and validation.
- **Hand-rolling secret encryption.** Don't fetch the public key and libsodium-encrypt yourself; `gh secret set` does it.
- **Guessing a `gh api` body.** Resolve the schema (Step 3b); field requirements vary by endpoint.
- **Loading the whole spec.** Don't `cat` the multi-MB OpenAPI JSON into context — scan the index, resolve one op.

## Output

This skill produces **GitHub side effects** (the requested operation) and returns the parsed result to the calling agent. It writes no files of its own (it only *consumes* the caller-injected credentials). For writes it reports the created/updated resource (number, URL, id); for reads it returns the result set, paginating as needed. The abstract consumer is the calling agent (or sub-agent) that needs the operation performed; the token never enters that output.

## Related

- [`references/auth.md`](references/auth.md) — the credential contract this skill consumes (caller-injected host + the ordered token-load rule), per-call `GH_TOKEN`, the verify probe, honest-secret handling.
- The CLI-first + `gh api`-fallback pattern (with a bundled OpenAPI spec) generalizes to other providers that ship a first-class CLI.

## Progressive disclosure

Heavy content lives in subfolders, loaded only on demand:

- [`references/auth.md`](references/auth.md) — the credential contract this skill consumes: caller-injected host, the ordered token-load rule, per-call `GH_TOKEN`, verify probe, the env bridge for example scripts. Load in Step 1.
- [`references/cli-reference.md`](references/cli-reference.md) — CLI-first detail: the decision rule, `--json`/`--jq` output, `gh secret set` (client-side encryption), using `cli-index.md` + live `gh --help`. Load in Steps 2–3a.
- [`references/gh-api.md`](references/gh-api.md) — the fallback: `gh api` flags (`-X`, `-f`/`-F`, `-H`, `--paginate`, `--slurp`, `--jq`, `--input`, `--hostname`), the index+resolver workflow, GraphQL, errors/scopes. Load in Step 3b.
- [`references/sources.md`](references/sources.md) — provenance (the `gh` manual + the bundled spec version).

**Added during augmentation (Phase 2.C), referenced above:**

- `assets/cli-index.md` — one line per `gh` command, for discovery (Step 2).
- `assets/github-openapi.json` — the bundled GitHub REST OpenAPI spec (authoritative; queried, never loaded wholesale).
- `assets/endpoint-index.md` — one line per REST operation, for discovery (Step 3b).
- `scripts/endpoint.py` + `scripts/endpoint.py.validation.md` — the `python3` `$ref`-resolver (Step 3b).
- `scripts/<example>.sh` + `.validation.md` — validated example `gh`/`gh api` calls.

## Standalone usage (optional, not required)

This is a convenience for a **human running the skill by hand** outside agent-flow — it is **not a dependency of the skill**. The skill's normative contract is caller-injection (Step 1); this appendix is only the manual-operator bridge.

To run by hand, populate `GH_TOKEN` (and optionally `GH_HOST` / `GH_REPO`) yourself from a `.service-accounts.yaml` record + its `.env` token, then run the scripts. An example record:

```yaml
accounts:
  - name: github-personal
    provider: github
    host: github.com
    token_env: GH_PERSONAL_TOKEN     # the var holding the token value; value lives in .env (gitignored)
```

```bash
set -a; source .env; set +a                 # loads $GH_PERSONAL_TOKEN, never prints it
export GH_TOKEN="$GH_PERSONAL_TOKEN"
export GH_REPO="OWNER/REPO"                  # optional: fills {owner}/{repo}
bash scripts/create-issue.sh "My title" "My body"
```

The value is referenced by name only, never printed; per-call `GH_TOKEN` still applies (no `gh auth switch`).

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap).
- Body ≤ ~500 lines / 5,000 tokens — kept in context every turn; detail lives in `references/`.
- `assets/github-openapi.json` is large (queried on disk, never loaded into context).
