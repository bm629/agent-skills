# Auth & credentials — `github-cli-ops`

The skill **reads** which account to act as from a file convention; `gh` holds the
token. The token value is read only by the `gh` subprocess (as `GH_TOKEN`), never
printed.

## Account record (non-secret, committable)

`<scope-root>/.service-accounts.yaml`:

```yaml
accounts:
  - name: github-personal
    provider: github
    host: github.com
    token_env: GH_PERSONAL_TOKEN     # the env var that holds the token value
    # user: octocat                  # optional, informational
```

- **Scope:** resolved at the **workspace root**, or `<workspace>/projects/<name>/`
  when working inside a project. The skill reads the nearest record.
- **Selection:** `--account=<name>`, or the sole `provider: github` entry.
- Multiple `github` records are allowed (one per account/host); each names its own
  `token_env`.

## Token value (secret, gitignored)

`<scope-root>/.env`:

```
GH_PERSONAL_TOKEN=ghp_xxx
```

- `.env` **must** be gitignored. The token value goes only here, never in the record.
- A classic PAT or a fine-grained token both work via `GH_TOKEN`.
- Scope it for the operations you run: e.g. `repo` (private repos, issues, PRs),
  `delete_repo`, `read:org`/`admin:org`, `workflow`, secrets. A 4xx is usually a
  missing scope — mint a token with the right ones rather than retrying.

## Per-call authentication (the core rule)

Prefix **every** `gh` invocation with the token; do not change global `gh` state:

```bash
GH_TOKEN="$GH_PERSONAL_TOKEN" gh issue list --repo OWNER/REPO
```

Verified from `gh help environment`: `GH_TOKEN` / `GITHUB_TOKEN` *"takes precedence
over previously stored credentials"*, per-invocation, for **all** `gh` commands
(including `gh api`). So per-call `GH_TOKEN` selects the account with **no**
`gh auth switch` and **no** global mutation.

- **Non-default / Enterprise host:** set `GH_HOST="$host"`, and for GitHub Enterprise
  Server use `GH_ENTERPRISE_TOKEN` instead of `GH_TOKEN`.
- **Verify the token works** before real operations:
  `GH_TOKEN="$<token_env>" gh api user --jq .login` → prints the authenticated login.
- When `GH_TOKEN` is set, `gh auth status` reports the env token and `gh auth
  login`/`switch` are bypassed — expected; it confirms per-call auth is in effect.

## The env bridge (for the example `scripts/*.sh`)

The example scripts expect the resolved token in `GH_TOKEN` and (optionally) a
`GH_REPO`. Bridge the record + `.env` into the environment first:

```bash
set -a; source <scope-root>/.env; set +a     # load the token value(s)
export GH_TOKEN="$GH_PERSONAL_TOKEN"          # bridge the record's token_env
export GH_REPO="OWNER/REPO"                    # optional: fills {owner}/{repo}
bash scripts/create-issue.sh "My title" "My body"
```

## Honest secret handling

- Never `echo`, print, or paste the token; never write it into the record.
- Reference it only as `$<token_env>` inside the `GH_TOKEN=…` prefix.
- The skill provisions nothing — creating the record + `.env` is the user's job.
