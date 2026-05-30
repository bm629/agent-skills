# Credentials — file convention (this skill READS, never writes)

Provisioning is a documented convention (or an optional credential-provisioning helper — not a dependency). This skill only reads the record + the token from the environment.

## Record (non-secret) + token (secret)

Record — `<scope-root>/.service-accounts.yaml` (committable; no secrets):
```yaml
accounts:
  - name: atlassian-work
    provider: atlassian
    base_url: https://workco.atlassian.net
    email: me@workco.com
    token_env: ATLASSIAN_WORK_API_TOKEN
```

Token value — `<scope-root>/.env` (**gitignored**):
```
ATLASSIAN_WORK_API_TOKEN=<api token from id.atlassian.com>
```

The token value lives **only** in `.env`. Never put it in the record. Ensure `.env` is gitignored.

## Scope resolution

`<scope-root>` = the workspace root, or `<workspace>/projects/<name>/` when working inside a project. Resolve via `--project=<name>` / `--workspace-only`, else walk up from the current directory. Same-name accounts in different scopes are independent entities.

## Account selection

`--account=<name>` picks the record; otherwise the sole `provider: atlassian` entry. Multiple accounts (work / personal / different sites) are supported.

## Honest-secret handling

The token value is read **only** by the `curl` subprocess from the environment:
```
curl -u "$email:$ATLASSIAN_WORK_API_TOKEN" ...
```
The agent never reads, prints, or logs the value. Get an API token at id.atlassian.com → Security → "Create API token".

## Loading the token + running the example scripts

The token lives in `.env` (a file) — load it into the environment before any `curl`:

```
set -a; source <scope-root>/.env; set +a   # sets $<token_env>, e.g. $ATLASSIAN_WORK_API_TOKEN
```

The resolved record gives `base_url`, `email`, and `token_env`. The example `scripts/*.sh` read three **fixed** env vars — bridge the record into them once per session:

```
export ATLASSIAN_EMAIL="<record.email>"
export ATLASSIAN_BASE_URL="<record.base_url>"
export ATLASSIAN_API_TOKEN="$<record.token_env>"   # e.g. "$ATLASSIAN_WORK_API_TOKEN"
```

Then run e.g. `bash scripts/create-confluence-page.sh <space-id> "<title>"`. The value is loaded by `source` and referenced by name only — never printed. (When building a `curl` by hand instead of via a script, use `$email` / `$base_url` / `$<token_env>` directly.)
