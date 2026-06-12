# Credentials — the contract this skill consumes (never provisions)

This skill is a pure **consumer** of caller-injected credentials. The caller has already resolved which account to act as and injected what the operation needs; this skill reads those values from context + the environment and uses them. It never reads a credential record, never selects an account, and never provisions anything.

## 1. The fields the caller injects

From context (not from a file), the operation receives:

- **`base_url`** — the Penpot origin, e.g. `https://design.penpot.app` (cloud) or your self-hosted host. The RPC path `/api/rpc/command/<command>` is appended to this; do not include it in `base_url`.
- **the capability** the account is acting under (informational; the caller has already authorized it — for this skill, `design`).

There is no `email`/`username` field — Penpot token auth identifies the account from the token alone.

## 2. The token — ordered load rule

The context carries the token's **variable NAME**, never its value. Resolve that name in this order:

1. the project-level **`.env` value** if that file exists and defines the var, **else**
2. the **environment variable** of that name.

Project `.env` is tried **first** — that is how a project `.env` overrides a global environment variable. This is **not** OS dotenv precedence (there is no in-repo dotenv loader); it is the skill's instructed load order. The file is the project **`.env`**, not `.envrc`. The project root is supplied by the caller/context; perform **no** scope resolution or directory walk to locate it. The token **value** never enters the context prose — only the variable name; the value reaches `curl` by being read from the `.env` file or the environment.

`.env` remains a valid secret store: `set -a; source <path>/.env; set +a` loads the named var into the environment (it loads, never prints).

## 3. The auth header + the bridge into the scripts

Penpot uses a personal access token in an `Authorization` header — **`Token`, not `Bearer`**:

```
Authorization: Token <token-value>
```

The example `scripts/*.sh` read two env vars: `base_url` and `PENPOT_TOKEN` (the token var name). Bridge the injected values once per session:

```
export base_url="<base_url>"            # e.g. https://design.penpot.app
export PENPOT_TOKEN="$<token var name>" # e.g. "$PENPOT_DESIGN_TOKEN" — value never printed
```

Then run e.g. `bash scripts/create-file.sh <project-uuid> "<name>"`. The value is referenced by name only — never printed. (When building a `curl` by hand instead of via a script, use `$base_url` and `$<token var name>` directly.)

## 4. Honest-secret handling

The token value is read **only** by the `curl` subprocess from the environment:

```
curl -sS -X POST "$base_url/api/rpc/command/get-profile" \
  -H "Authorization: Token $PENPOT_TOKEN" -d '{}'
```

The agent never reads, prints, or logs the value, and never writes it anywhere.

A Penpot access token is created in the UI at **Your account → Access tokens → Generate new token** (name + expiration: Never / 30 / 60 / 90 / 180 days). It is shown **once** at creation. There is **no scoping** — a token carries the full access of the owning account, so treat it like a password and prefer a short expiry for automation.
