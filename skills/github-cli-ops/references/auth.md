# Auth & credentials — `github-cli-ops`

This skill is a pure **consumer** of caller-injected credentials. The caller (e.g. the agent-flow spine) has already resolved which account to act as and injected what the operation needs; this skill reads those values from context + the environment and uses them per-call. It never reads a credential record, never selects an account, and never provisions anything. The token value is read only by the `gh` subprocess (as `GH_TOKEN`), never printed.

## 1. The fields the caller injects

From context (not from a file), the operation receives:

- **`host`** — the GitHub host, default `github.com` (an Enterprise host sets `GH_HOST`).
- **the capability** the account is acting under (informational; the caller has already authorized it).

## 2. The token — ordered load rule

The context carries the token's **variable NAME**, never its value. Resolve that name in this order:

1. the project-level **`.env` value** if that file exists and defines the var, **else**
2. the **environment variable** of that name.

Project `.env` is tried **first** — that is how a project `.env` overrides a global environment variable. This is **not** OS dotenv precedence (there is no in-repo dotenv loader); it is the skill's instructed load order. The file is the project **`.env`**, not `.envrc`. The project root is supplied by the caller/context; perform **no** scope resolution or directory walk to locate it. The token **value** never enters the context prose — only the variable name; only the `gh` subprocess reads the value, via `GH_TOKEN`.

`.env` remains a valid secret store: `set -a; source <path>/.env; set +a` loads the named var into the environment (it loads, never prints). A classic PAT or a fine-grained token both work via `GH_TOKEN`. Scope it for the operations you run (e.g. `repo`, `delete_repo`, `read:org`/`admin:org`, `workflow`, secrets); a 4xx is usually a missing scope, not a skill bug.

## 3. The env bridge (into `GH_TOKEN` / `GH_HOST` / `GH_REPO`)

The example `scripts/*.sh` expect the resolved token in `GH_TOKEN` and (optionally) a `GH_HOST` / `GH_REPO`. Bridge the injected fields into the environment first:

```bash
set -a; source <path>/.env; set +a            # load the token value (by its var name)
export GH_TOKEN="$<token var name>"            # e.g. "$GH_PERSONAL_TOKEN"
export GH_HOST="<host>"                         # only for a non-default / Enterprise host
export GH_REPO="OWNER/REPO"                      # optional: fills {owner}/{repo}
bash scripts/create-issue.sh "My title" "My body"
```

## 4. Per-call authentication (the core rule, kept)

Prefix **every** `gh` invocation with the token; do not change global `gh` state:

```bash
GH_TOKEN="$<token var name>" gh issue list --repo OWNER/REPO
```

Verified from `gh help environment`: `GH_TOKEN` / `GITHUB_TOKEN` *"takes precedence over previously stored credentials"*, per-invocation, for **all** `gh` commands (including `gh api`). So per-call `GH_TOKEN` selects the account with **no** `gh auth switch` and **no** global mutation.

- **Non-default / Enterprise host:** set `GH_HOST="<host>"`, and for GitHub Enterprise Server use `GH_ENTERPRISE_TOKEN` instead of `GH_TOKEN`.
- **Verify the token works** before real operations: `GH_TOKEN="$<token var name>" gh api user --jq .login` → prints the authenticated login.
- When `GH_TOKEN` is set, `gh auth status` reports the env token and `gh auth login`/`switch` are bypassed — expected; it confirms per-call auth is in effect.

## 5. Honest-secret handling

- Never `echo`, print, or paste the token; never write its value into any file.
- Reference it only as `$<token var name>` inside the `GH_TOKEN=…` prefix.
- The skill provisions nothing — credentials are provided by the caller.
