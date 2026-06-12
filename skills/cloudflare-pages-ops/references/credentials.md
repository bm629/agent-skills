# Credentials — the contract this skill consumes (never provisions)

This skill is a pure **consumer** of caller-injected credentials. The caller has already resolved which account to act as and injected what the operation needs; this skill reads those values and uses them. It never reads a credential record, never selects an account, never runs `wrangler login`, and never provisions anything.

## 1. The fields the caller injects

From context (not from a file), the operation receives:

- **`account_id`** — the Cloudflare account id. **Non-secret** — it is a plain context value (like a base URL), interpolated into the REST path `/accounts/{account_id}/pages/...` and exported as `CLOUDFLARE_ACCOUNT_ID` for Wrangler. It does **not** go through the token-load rule.
- **the capability** the account is acting under (informational; the caller has already authorized it — for this skill, `web-hosting`).
- **the token's variable NAME** (see §2).

## 2. The token — ordered load rule

The context carries the token's **variable NAME**, never its value. Resolve that name in this order:

1. the project-level **`.env` value** if that file exists and defines the var, **else**
2. the **environment variable** of that name.

Project `.env` is tried **first** — that is how a project `.env` overrides a global environment variable. This is **not** OS dotenv precedence (there is no in-repo dotenv loader); it is the skill's instructed load order. The file is the project **`.env`**, not `.envrc`. The project root is supplied by the caller/context; perform **no** scope resolution or directory walk to locate it. The token **value** never enters the context prose — only the variable name; the value reaches the Wrangler / `curl` subprocess only via the environment.

`.env` remains a valid secret store: `set -a; source <path>/.env; set +a` loads the named var into the environment (it loads, never prints).

## 3. The auth + the bridge

Cloudflare Pages auth is a **scoped API token** sent as `Authorization: Bearer <token>` (the legacy `X-Auth-Key`/`X-Auth-Email` global-key pair is **not** used). Two consumers, both reading the value from the environment:

- **Wrangler (CLI):** reads `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID`. With both set it runs headlessly — **never** `wrangler login`.
- **REST:** `Authorization: Bearer $CLOUDFLARE_API_TOKEN` against `https://api.cloudflare.com/client/v4/accounts/<account_id>/pages/...`.

Bridge once per session:

```
export CLOUDFLARE_ACCOUNT_ID="<account_id>"        # the non-secret context field
export CLOUDFLARE_API_TOKEN="$<token var name>"    # e.g. "$CLOUDFLARE_PAGES_TOKEN" — never printed
```

## 4. Honest-secret handling

The token value is read **only** by the Wrangler / `curl` subprocess from the environment:

```
curl -sS -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/pages/projects"
```

The agent never reads, prints, or logs the value, and never writes it anywhere. A missing token is a hard caller error — **not** a cue to run `wrangler login`.

A scoped token is created at **My Profile → API Tokens → Create Token**, with the **Cloudflare Pages → Edit** permission (account-scoped). It is a long-lived static token (no OAuth/refresh); the secret is shown **once** at creation. Prefer a revocable, short-lived token for automation.
