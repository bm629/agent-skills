# Credentials — the contract this skill consumes (never provisions)

This skill is a pure **consumer** of caller-injected credentials. The caller has already resolved which account to act as and injected what the operation needs; this skill reads the token from the environment and uses it. It never reads a credential record, never selects an account, never runs `netlify login`, and never provisions anything.

## 1. The fields the caller injects

Netlify carries **no non-secret record field** beyond the token — no base URL (the API host `api.netlify.com` is fixed), no account id, no email. From context the operation receives only:

- **the capability** the account is acting under (informational; the caller has already authorized it — for this skill, `web-hosting`).
- **the token's variable NAME** (see §2).

## 2. The token — ordered load rule

The context carries the token's **variable NAME**, never its value. Resolve that name in this order:

1. the project-level **`.env` value** if that file exists and defines the var, **else**
2. the **environment variable** of that name.

Project `.env` is tried **first** — that is how a project `.env` overrides a global environment variable. This is **not** OS dotenv precedence (there is no in-repo dotenv loader); it is the skill's instructed load order. The file is the project **`.env`**, not `.envrc`. The project root is supplied by the caller/context; perform **no** scope resolution or directory walk to locate it. The token **value** never enters the context prose — only the variable name; the value reaches the `netlify` CLI / `curl` only via the environment.

`.env` remains a valid secret store: `set -a; source <path>/.env; set +a` loads the named var into the environment (it loads, never prints).

## 3. The auth + the bridge

Netlify auth is a **Bearer personal access token**. Two consumers, both reading the value from the environment:

- **CLI:** the `netlify` CLI reads `NETLIFY_AUTH_TOKEN` (or accepts `--auth <token>`). Bridge the injected token var into it: `export NETLIFY_AUTH_TOKEN="$<token var name>"`. With the token present the CLI runs headlessly — **never** `netlify login` / `netlify logout` in an agent flow.
- **REST:** send `Authorization: Bearer $<token var name>` against `https://api.netlify.com/api/v1`.

The example `scripts/*.sh` read `NETLIFY_AUTH_TOKEN`. Bridge once per session:

```
export NETLIFY_AUTH_TOKEN="$<token var name>"   # e.g. "$NETLIFY_PROD_TOKEN" — value never printed
```

## 4. Honest-secret handling

The token value is read **only** by the `netlify` CLI / `curl` subprocess from the environment:

```
curl -sS -H "Authorization: Bearer $NETLIFY_AUTH_TOKEN" "https://api.netlify.com/api/v1/sites"
```

The agent never reads, prints, or logs the value, and never writes it anywhere. The **absence** of the injected token is a hard caller error — **not** a cue to prompt the user or run `netlify login`.

A Netlify PAT is created in the UI at **User → Applications → Personal access tokens → New access token** (an expiration date is required; the value is shown **once**). Tokens carry the owning user's access (coarse scoping) and are invalidated by a password reset — prefer a revocable, short-lived token for automation.
