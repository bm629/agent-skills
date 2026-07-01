---
# ─── UNIVERSAL CORE ──────────────────────────────────────────────────────
name: atlassian-rest-ops
description: >
  Use when calling the Atlassian Cloud REST API directly — Confluence
  Cloud v2 (pages, spaces, search) or Jira Cloud v3 (issues, JQL search,
  comments) — to perform operations programmatically, including writes such
  as creating a Confluence page. Calls REST with curl (no SDK, no pip),
  authenticating with a Cloud email + API token. Constructs any of the
  800+ endpoints from a bundled OpenAPI spec via an endpoint index + a
  $ref-resolver, with per-API patterns (base URL, pagination, errors,
  rate limits) and the ADF / storage rich-text formats handled
  explicitly. Consumes caller-injected credentials (base_url, email, and
  a token resolved by variable name) — it does not provision or resolve
  them; the token value is read only by curl, never printed.

# ─── PROVIDER-SPECIFIC EXTENSIONS ────────────────────────────────────────
extensions:
  claude:
    allowed-tools: [Read, Write, Edit, Grep, Glob, Bash]
    user-invocable: true
    when_to_use: "performing a Confluence/Jira Cloud REST operation directly via the API"
    argument-hint: "<operation, e.g. 'create a Confluence page'>"
  copilot: {}
  cursor:
    alwaysApply: false
    globs: []
  gemini: {}
  codex: {}

version: "1.1.0"

forge:
  status: reviewed
  forged: 2026-05-31
  reviewed: 2026-06-12
---

# atlassian-rest-ops

## Overview

This skill lets an agent perform **any** Confluence Cloud (v2) or Jira Cloud (v3) operation by calling the **REST API directly with `curl`** — no SDK, no `pip` dependency. The REST API is the complete API surface, including writes such as creating a Confluence page. The agent consumes the credentials the caller injected, looks up an endpoint in a bundled OpenAPI spec via an **endpoint index + a `$ref`-resolver**, constructs the `curl`, and parses the JSON. Confluence and Jira differ on several axes (base URL, pagination, errors, rich-text), so this skill carries **per-API** patterns rather than one generic shape.

## When to activate

- ✅ Performing a Confluence Cloud v2 operation (create/get/update/search pages, spaces, attachments, …).
- ✅ Performing a Jira Cloud v3 operation (create/search/transition issues, comments, …).
- ✅ A write or operation you need done programmatically against the Atlassian REST API (e.g. creating a Confluence page).

**Do NOT activate when:**

- The target is Atlassian **Server / Data Center** (this skill is Cloud + API-token only).
- You only need credential setup — credentials are provided by the caller; this skill does not provision or resolve them (see `references/credentials.md` for the contract it consumes).

## Workflow

### Step 1 — Receive the injected credentials

The caller has already resolved the account and injected what this operation needs — **consume** it; do **not** look for a record yourself. You receive from context:

- **`base_url`** and **`email`** (and the **capability** the account acts under) — as context values, not read from a file.
- **The token, by an ordered load rule** the context carries the **variable NAME** for. Resolve that name as: the project-level **`.env` value if that file exists** and defines the var, **else** the **environment variable** of that name — project `.env` is tried first (that is how a project `.env` overrides a global env var). The token **value** is never in the context prose — only its variable name; `curl` reads the value from the environment. The project root is supplied by the context; perform **no** scope resolution or directory walk to find the `.env`, and it is project `.env`, not `.envrc`.

Then bridge these into the example scripts' fixed vars `ATLASSIAN_EMAIL` / `ATLASSIAN_BASE_URL` / `ATLASSIAN_API_TOKEN` (same bridge as before; only the inputs now come from context). Full contract + the bridge: [`references/credentials.md`](references/credentials.md).

### Step 2 — Find the endpoint

Scan [`assets/endpoint-index.md`](assets/) (one line per operation: `METHOD path — summary (operationId)`) for the operation you need. Never load a full spec into context — they are multi-MB.

### Step 3 — Resolve the call shape

Run the resolver: `python3 scripts/endpoint.py <confluence|jira> <operationId>`. It dereferences that one operation from the bundled OpenAPI spec (`$ref`-resolved) and prints the method, path, params, request/response schema, and a `curl` skeleton. (`scripts/endpoint.py` + its validation are added during augmentation; see Progressive disclosure.)

### Step 4 — Construct + run the `curl`

Apply the **per-API** patterns from [`references/patterns.md`](references/patterns.md):

- **Auth** (both): `curl -u "$email:$<token_env>"` (HTTP Basic).
- **Base URL:** Confluence → `<base_url>/wiki/api/v2/<path>`; Jira → `<base_url>/<path>` (paths already include `/rest/api/3/…`).
- **Rich-text bodies** (the easy-to-get-wrong part) — see [`references/rich-text.md`](references/rich-text.md): Jira uses **ADF as a raw JSON object**; Confluence uses `{representation, value}` where `atlas_doc_format` means the ADF JSON **stringified** and `storage` means an XHTML string. If your source is **Markdown** (e.g. a formatted comment), convert it to ADF with `python3 scripts/md_to_adf.py < body.md` rather than sending the raw Markdown (which renders `##`/`**`/`|` literally).
- Send/accept `application/json`.

### Step 5 — Handle the response

- **Pagination:** Confluence → cursor + follow `_links.next`; Jira → `startAt`/`maxResults` (+ `total`/`isLast`), or `nextPageToken` on newer endpoints. See `references/patterns.md`.
- **Errors:** Jira returns `ErrorCollection` `{errorMessages, errors, status}`; Confluence returns inline error JSON. On HTTP 429 (Jira) back off and retry.

## Rules

**Hard rules (never violate):**

- **No SDK, no `pip`.** API calls use `curl`; the only helper is `scripts/endpoint.py` (`python3` **stdlib** only).
- **Never read or print the token value.** Reference it only as `$<token_env>` in a `curl -u` argument; the subprocess reads it from the environment. The token lives only in `.env` (gitignored).
- **Resolve before constructing.** Build a request body/params from the `$ref`-resolved schema (Step 3) or the verified rich-text formats — never from a guessed/remembered field set.
- **Per-API, not generic.** Apply Confluence vs Jira patterns correctly (base URL, pagination, rich-text, errors) — they differ.
- **Rich-text:** Jira ADF = raw object; Confluence `atlas_doc_format` = stringified ADF in `value`. Do not mix them.
- **This skill never writes credentials.** Credentials are provided by the caller; this skill never provisions or resolves them.

**Preferences (override-able):**

- Prefer the newer Jira issue search `GET /rest/api/3/search/jql` (`nextPageToken`) over the legacy `/search` (`startAt`).
- Request only needed fields (`fields=` on Jira, `body-format=` on Confluence) to keep responses small.

## Gotchas

- **Rich-text mismatch.** Sending a raw ADF object to Confluence `atlas_doc_format` (instead of a stringified one), or a stringified blob to Jira (instead of a raw object), is the most common failure. Confluence `value` is **always a string**.
- **Base-URL difference.** Confluence paths are relative to `…/wiki/api/v2`; Jira paths already include `/rest/api/3`. Don't double-prefix or drop `/wiki`.
- **`$ref` chains.** The request body is rarely inline in the spec — it `$ref`s a schema (which may `$ref` further). Use the resolver (Step 3); a raw `grep` of the spec won't give you the full shape.
- **Legacy vs new Jira search.** `GET /rest/api/3/search` is being deprecated for `GET /rest/api/3/search/jql`; pagination differs (`startAt` vs `nextPageToken`).
- **Rate limits.** Jira returns HTTP 429 with a `Retry-After`; honor it. Confluence may return 413 on oversized bodies.
- **Confluence delete is two-stage** (verified live, applies to **pages, blogposts, and other content**). `DELETE /pages/{id}` (or `/blogposts/{id}`) only **trashes** it (returns 204, but `GET` still returns it with `status: trashed`). To remove permanently, call `DELETE /<type>/{id}?purge=true` — which only works **once trashed** (purge-without-trash is a no-op). A plain delete is not full removal.
- **Jira `/search/jql` rejects unbounded JQL** (verified live). Ordering-only or empty JQL → `400 ErrorCollection` ("Unbounded JQL queries are not allowed here"). Always include a search restriction (e.g. `project = X`, `created >= -30d`).

## Anti-patterns

- **Guessing the body.** Don't hand-write a request body from memory of "what Jira issues look like" — resolve the schema; field requirements change per project/screen.
- **Echoing the token.** Never `echo $TOKEN`, never paste it into a command you print, never write its value into any file. Reference the env var inside `curl` only.
- **Loading the whole spec.** Don't `cat`/read the multi-MB OpenAPI JSON into context — scan the index, resolve one op.
- **One-size-fits-all.** Don't apply Jira's pagination/errors/ADF to Confluence or vice-versa.
- **SDK creep.** Don't reach for `atlassian-python-api` / `pip install` — `curl` + the resolver cover every endpoint.

## Output

This skill produces **API side effects** (the requested Confluence/Jira operation) and returns the parsed JSON response to the calling agent. It writes no files of its own (it only *consumes* the caller-injected credentials). For write operations it reports the created/updated resource (id, key, URL); for reads it returns the result set, following pagination as needed. The abstract consumer is the calling agent (or a sub-agent) that needs the operation performed; secrets never enter that output.

## Related

- [`references/credentials.md`](references/credentials.md) — the credential contract this skill consumes (caller-injected fields + the ordered token-load rule + the bridge into the fixed vars).
- The REST-direct + bundled-OpenAPI-spec pattern generalizes to other API providers.

## Progressive disclosure

Heavy content lives in subfolders, loaded only on demand:

- [`references/patterns.md`](references/patterns.md) — per-API patterns: auth, base URL, pagination (Confluence cursor vs Jira offset/token), response envelopes, errors, rate limits, `expand`. Load in Steps 4–5.
- [`references/rich-text.md`](references/rich-text.md) — ADF (Jira, raw object) and Confluence body representations (`storage` / `atlas_doc_format`, value-as-string) with worked examples + the cross-API gotcha. Load when building a request body.
- [`references/credentials.md`](references/credentials.md) — the credential contract this skill consumes: caller-injected fields, the ordered token-load rule, the bridge into the fixed vars, honest-secret handling. Load in Step 1.
- [`references/sources.md`](references/sources.md) — provenance (Atlassian official docs + the bundled spec versions).

**Added during augmentation (Phase 2.C), referenced above:**

- `assets/confluence-v2.json`, `assets/jira-v3.json` — the bundled OpenAPI specs (authoritative; queried, never loaded wholesale).
- `assets/endpoint-index.md` — one line per operation, for discovery (Step 2).
- `scripts/endpoint.py` + `scripts/endpoint.py.validation.md` — the `python3` `$ref`-resolver (Step 3).
- `scripts/<op>.sh` + `.validation.md` — the four validated example `curl`s (create Confluence page, Confluence list, Jira create issue, Jira search).
- `scripts/md_to_adf.py` + `.validation.md` — a stdlib Markdown -> ADF converter. Pipe a Markdown comment/description through it to post it as native ADF (headings, bold, code, links, lists, GFM tables render instead of showing raw `##`/`|`): `python3 scripts/md_to_adf.py < comment.md` -> the ADF object for the Jira `{"body": ...}`.

## Standalone usage (optional, not required)

This is a convenience for a **human running the skill by hand** outside agent-flow — it is **not a dependency of the skill**. The skill's normative contract is caller-injection (Step 1); this appendix is only the manual-operator bridge.

To run by hand, populate the three fixed vars yourself from a `.service-accounts.yaml` record + its `.env` token, then run the scripts. An example record:

```yaml
accounts:
  - name: atlassian-work
    provider: atlassian
    base_url: https://workco.atlassian.net
    email: me@workco.com
    token_env: ATLASSIAN_WORK_API_TOKEN     # the var holding the token value; value lives in .env (gitignored)
```

```bash
set -a; source .env; set +a                 # loads $ATLASSIAN_WORK_API_TOKEN, never prints it
export ATLASSIAN_EMAIL="me@workco.com"
export ATLASSIAN_BASE_URL="https://workco.atlassian.net"
export ATLASSIAN_API_TOKEN="$ATLASSIAN_WORK_API_TOKEN"
bash scripts/create-confluence-page.sh <space-id> "<title>"
```

Get an API token at id.atlassian.com → Security → "Create API token". The value is referenced by name only, never printed.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap).
- Body ≤ ~500 lines / 5,000 tokens — kept in context every turn; per-API detail lives in `references/`.
- `assets/*.json` are large (queried on disk, never loaded into context).
