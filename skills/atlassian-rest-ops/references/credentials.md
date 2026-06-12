# Credentials — the contract this skill consumes (never provisions)

This skill is a pure **consumer** of caller-injected credentials. The caller (e.g. the agent-flow spine) has already resolved which account to act as and injected what the operation needs; this skill reads those values from context + the environment and uses them. It never reads a credential record, never selects an account, and never provisions anything.

## 1. The fields the caller injects

From context (not from a file), the operation receives:

- **`base_url`** — the Atlassian site, e.g. `https://workco.atlassian.net`.
- **`email`** — the Cloud account email for HTTP Basic auth.
- **the capability** the account is acting under (informational; the caller has already authorized it).

## 2. The token — ordered load rule

The context carries the token's **variable NAME**, never its value. Resolve that name in this order:

1. the project-level **`.env` value** if that file exists and defines the var, **else**
2. the **environment variable** of that name.

Project `.env` is tried **first** — that is how a project `.env` overrides a global environment variable. This is **not** OS dotenv precedence (there is no in-repo dotenv loader); it is the skill's instructed load order. The file is the project **`.env`**, not `.envrc`. The project root is supplied by the caller/context; perform **no** scope resolution or directory walk to locate it. The token **value** never enters the context prose — only the variable name; the value reaches `curl` by being read from the `.env` file or the environment.

`.env` remains a valid secret store: `set -a; source <path>/.env; set +a` loads the named var into the environment (it loads, never prints).

## 3. The bridge into the fixed env vars

The example `scripts/*.sh` read three **fixed** env vars. Bridge the injected fields into them once per session:

```
export ATLASSIAN_EMAIL="<email>"
export ATLASSIAN_BASE_URL="<base_url>"
export ATLASSIAN_API_TOKEN="$<token var name>"   # e.g. "$ATLASSIAN_WORK_API_TOKEN"
```

Then run e.g. `bash scripts/create-confluence-page.sh <space-id> "<title>"`. The value is referenced by name only — never printed. (When building a `curl` by hand instead of via a script, use `$email` / `$base_url` / `$<token var name>` directly.)

## 4. Honest-secret handling

The token value is read **only** by the `curl` subprocess from the environment:

```
curl -u "$email:$ATLASSIAN_API_TOKEN" ...
```

The agent never reads, prints, or logs the value, and never writes it anywhere. Get an API token at id.atlassian.com → Security → "Create API token".
