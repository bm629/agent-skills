# Credentials — the contract this skill consumes (never provisions)

This skill is a pure **consumer** of caller-injected credentials. The caller has already resolved which account to act as and injected what the operation needs; this skill reads those values from context + the environment and uses them. It never reads a credential record, never selects an account, and never provisions anything.

## 1. The fields the caller injects

From context (not from a file), the operation receives:

- **`base_url`** — the Jenkins origin, e.g. `https://jenkins.example.com`. Paths like `job/<name>/build` are appended to this.
- **`username`** — the Jenkins user the API token belongs to (HTTP Basic auth identity).
- **the capability** the account is acting under (informational; the caller has already authorized it — for this skill, `cicd`).

## 2. The token — ordered load rule

The context carries the token's **variable NAME**, never its value. Resolve that name in this order:

1. the project-level **`.env` value** if that file exists and defines the var, **else**
2. the **environment variable** of that name.

Project `.env` is tried **first** — that is how a project `.env` overrides a global environment variable. This is **not** OS dotenv precedence (there is no in-repo dotenv loader); it is the skill's instructed load order. The file is the project **`.env`**, not `.envrc`. The project root is supplied by the caller/context; perform **no** scope resolution or directory walk to locate it. The token **value** never enters the context prose — only the variable name; the value reaches `curl` by being read from the `.env` file or the environment.

`.env` remains a valid secret store: `set -a; source <path>/.env; set +a` loads the named var into the environment (it loads, never prints).

## 3. The auth + the bridge into the scripts

Jenkins REST auth is **HTTP Basic** with a per-user **API token** (not the login password — the official docs discourage the password):

```
curl -u "$username:$<token-value>" ...
```

The example `scripts/*.sh` read three env vars: `base_url`, `username`, and `JENKINS_TOKEN` (the token var name). Bridge the injected values once per session:

```
export base_url="<base_url>"            # e.g. https://jenkins.example.com
export username="<username>"
export JENKINS_TOKEN="$<token var name>" # e.g. "$JENKINS_CI_TOKEN" — value never printed
```

Then run e.g. `bash scripts/trigger-build.sh <job> BRANCH=main`. The value is referenced by name only — never printed. (When building a `curl` by hand, use `-u "$username:$<token var name>"` directly.)

## 4. Honest-secret handling

The token value is read **only** by the `curl` subprocess from the environment:

```
curl -sS -u "$username:$JENKINS_TOKEN" "$base_url/api/json"
```

The agent never reads, prints, or logs the value, and never writes it anywhere.

A Jenkins API token is created at **your user page → Configure → API Token → Add new token** (`<base_url>/me/configure`). It is shown **once** (stored SHA-256-hashed), can be named/revoked individually, and carries the **full authority of the owning user** (no per-endpoint scoping) — treat it like a password and prefer a revocable, short-lived token for automation.
