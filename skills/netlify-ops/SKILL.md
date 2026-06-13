---
# ─── UNIVERSAL CORE ──────────────────────────────────────────────────────
name: netlify-ops
description: >
  Use when driving Netlify web-hosting directly — creating a site, deploying
  a build (draft or production), setting + verifying a custom domain, reading
  deploy status, and listing/inspecting sites/deploys/DNS. CLI-first on the
  `netlify` CLI (which reads NETLIFY_AUTH_TOKEN and runs headlessly — never
  `netlify login`) with a REST fallback on Netlify's official OpenAPI at
  https://api.netlify.com/api/v1 (Authorization: Bearer <token>). Resolves any
  of the ~174 REST operations from a bundled spec via an endpoint index + a
  $ref-resolver, with the digest-deploy protocol, rate limits, and site_id
  conventions handled explicitly. Consumes caller-injected credentials (a token
  resolved by variable name) — it does not provision or resolve them; the token
  value is read only by the CLI/curl subprocess, never printed. For Netlify
  static/JAMstack + serverless hosting, not full-stack container apps.

# ─── PROVIDER-SPECIFIC EXTENSIONS ────────────────────────────────────────
extensions:
  claude:
    allowed-tools: [Read, Write, Edit, Grep, Glob, Bash]
    user-invocable: true
    when_to_use: "performing a Netlify web-hosting operation (site/deploy/domain) via the CLI or REST API"
    argument-hint: "<operation, e.g. 'deploy ./dist to site X in production'>"
  copilot: {}
  cursor:
    alwaysApply: false
    globs: []
  gemini: {}
  codex: {}

version: "1.0.0"

forge:
  status: reviewed
  forged: 2026-06-12
  reviewed: 2026-06-13
---

# netlify-ops

## Overview

This skill lets an agent perform Netlify web-hosting operations **CLI-first** (the `netlify` CLI) with a **REST fallback** on Netlify's official API — no SDK. The CLI is the ergonomic common path (create a site, deploy a directory, read status); the REST API is the comprehensive long tail (custom domains, fine-grained reads, DNS), grounded on a bundled OpenAPI via an endpoint index + a `$ref`-resolver so coverage never loads the spec into context. The agent consumes the caller-injected token, picks the CLI command or REST operation, runs it, and parses the JSON. It drives Netlify's static/JAMstack + serverless surface — not full-stack container hosting.

## When to activate

- ✅ Creating a Netlify **site**, or deploying a build to one (draft/preview or `--prod`).
- ✅ Setting + verifying a **custom domain**, or configuring a site's **DNS**.
- ✅ Reading **deploy status** (the `state` field) or listing/inspecting sites/deploys.

**Do NOT activate when:**

- You need **full-stack container/app hosting** (Render, Fly.io, Railway, Vercel SSR-as-PaaS) — Netlify here is a static/JAMstack + serverless-function host only.
- You only need credential setup — credentials are provided by the caller; this skill does not provision or resolve them, and never runs `netlify login` (see `references/credentials.md`).

## Workflow

### Step 1 — Receive the injected credentials

The caller has already resolved the account and injected the token — **consume** it; do **not** look for a record or log in. Netlify has **no non-secret record field** (the host is fixed; no account id/email). You receive from context the capability (`web-hosting`) and the token's **variable NAME**. Resolve that name as the project-level **`.env` value if that file exists** and defines the var, **else** the **environment variable** of that name (project `.env` first). The token **value** is never in context prose — only its variable name. Perform **no** scope resolution or directory walk; it is project `.env`, not `.envrc`.

Bridge the token into `NETLIFY_AUTH_TOKEN` (the CLI reads it; the REST fallback sends `Authorization: Bearer`). Never `netlify login`/`logout`. Full contract: [`references/credentials.md`](references/credentials.md).

### Step 2 — Pick the common path (CLI) or the long tail (REST)

- **CLI (common path):** scan [`assets/cli-index.md`](assets/) for `sites:create`, `deploy`, `status`, `sites:list`, and the `netlify api <operationId> --data` escape hatch. Detail: [`references/cli-reference.md`](references/cli-reference.md).
- **REST (long tail):** scan [`assets/endpoint-index.md`](assets/) (one line per operation), then `python3 scripts/endpoint.py <operationId>` to resolve params + body + a curl skeleton. Detail: [`references/rest-api.md`](references/rest-api.md). Never load the ~690 KB spec into context.

### Step 3 — Run it

The four bundled scripts cover the priority ops:

- `create-site.sh <name> [account-slug]` — `netlify sites:create … --json` (returns the site; its id is the `id` field — `--json` keys it as `id`, not `site_id` — pass that id as `--site` to deploy).
- `deploy.sh <site-id> <dir> [--prod]` — `netlify deploy --dir … --site … --json` (draft by default; `--prod` publishes).
- `set-custom-domain.sh <site-id> <domain>` — REST `PATCH updateSite` (`custom_domain`).
- `deploy-status.sh <site-id> <deploy-id>` — `getSiteDeploy` (the `state` field).

For anything else: CLI command from `cli-index.md`, or a `curl` against the resolved REST op.

### Step 4 — Handle the response

- **Deploys are async + multi-stage.** Pull the deploy id from `deploy.sh`'s `--json` output (the `deploy_id` / `id` field) to feed `deploy-status.sh`. A deploy moves `building → uploading → processing → ready` (or `error`). Poll `deploy-status.sh` (or `getSiteDeploy`) until `state` is terminal; a draft deploy has a unique preview URL, `--prod` publishes to the live site.
- **Custom domain ≠ DNS.** Setting `custom_domain` does not make it resolve — follow with DNS config (`configureDNSForSite` / `dns_zones` records).
- **Errors / limits:** non-2xx JSON; rate limits are 500 req/min general and **deploys 3/min · 100/day** — honor the `X-RateLimit-*` headers. A `401` means a missing/expired token.

## Rules

**Hard rules (never violate):**

- **Never `netlify login` / `netlify logout`.** Auth is the injected token via `NETLIFY_AUTH_TOKEN` (or `--auth`); the CLI runs headlessly. A missing token is a hard caller error, not a cue to log in.
- **Never read or print the token value.** Reference it only as `$NETLIFY_AUTH_TOKEN` (CLI env) or `Bearer $NETLIFY_AUTH_TOKEN` (REST); the subprocess reads it from the environment. The token lives only in `.env` (gitignored) or the environment.
- **Resolve before constructing a REST call.** Build a body/params from the `$ref`-resolved schema (`endpoint.py`) — never from a guessed field set.
- **Deploy to a known `site_id` with `--site`.** A fresh checkout has no `.netlify/state.json`; never rely on link state, never use `--allow-anonymous`.
- **CLI-first, REST for the tail.** Use the CLI for create/deploy/status; drop to REST for custom domain, DNS, and fine-grained reads.
- **This skill never writes credentials.** Credentials are provided by the caller.

**Preferences (override-able):**

- Pass `--json` (machine output) and `--force` (skip prompts) to the CLI for non-interactive use.
- For body-carrying REST writes (`updateSite`, `createSiteDeploy`) prefer the pure `curl` over the `netlify api` escape hatch (the escape-hatch body-key convention is unverified); use the escape hatch for path-params-only ops.
- Prefer the CLI `netlify deploy --dir` over the hand-rolled digest protocol — it does the SHA1 diff + upload for you.

## Gotchas

- **Don't log in.** The single biggest contract violation: reaching for `netlify login` when the token "isn't working." A bad token is an error to surface, not a login to perform.
- **`--no-build`, not `--build`.** The CLI builds by default; there is no `--build` flag — opt out with `--no-build`.
- **Draft vs prod.** Omitting `--prod` gives a draft/preview deploy (unique URL, production untouched). Only `--prod` publishes to the live site.
- **`site_id` is the key.** `--name`/`--account-slug` are human-facing; every API op keys on the opaque `site_id` (in `.netlify/state.json` after a link). Note: `sites:create --json` returns this id under `id`, not `site_id` (`.site_id` is null on create) — read `.id` from create output and pass it as `--site`.
- **The digest-deploy required-files step.** A hand-rolled REST `createSiteDeploy` returns a `required` array of SHA1s you must then upload — skip it and the deploy never reaches `ready`. The CLI handles this.
- **Custom domain needs DNS.** `updateSite` sets `custom_domain`; the domain only resolves once DNS is configured.
- **Rate limits bite deploys.** 3 deploys/min, 100/day — back off on `X-RateLimit-Remaining: 0`.
- **`state` is a free string.** The spec doesn't enumerate deploy states; treat the value list as from docs and confirm against a live deploy.

## Anti-patterns

- **Running `netlify login`.** Forbidden — the contract injects the token; never resolve your own auth or prompt the user to log in.
- **Echoing the token.** Never `echo $NETLIFY_AUTH_TOKEN`, never paste it into a printed command, never write its value to a file. Reference the env var only.
- **Guessing a REST body.** Resolve `updateSite` / `createSiteDeploy` with `endpoint.py` — don't hand-write a body from memory.
- **Deploying without `--site`.** Relying on link state in a fresh checkout silently deploys to the wrong (or no) site. Always pass `site_id`.
- **Using `--allow-anonymous`.** That creates a claimable site without auth — not this skill's path; always deploy to a known site with the injected token.
- **Loading the whole spec.** Don't `cat` the ~690 KB OpenAPI — scan the index, resolve one op.

## Output

This skill produces **CLI/API side effects** (the requested Netlify operation) and returns the parsed JSON to the calling agent. It writes no files of its own (it only *consumes* the caller-injected token). For a deploy it reports the deploy id + URL + terminal `state`; for a site it reports the `site_id` + URL; for reads it returns the requested JSON. The abstract consumer is the calling agent (or a sub-agent) that needs the web-hosting operation performed; secrets never enter that output.

## Related

- [`references/credentials.md`](references/credentials.md) — the credential contract (token-by-name → `NETLIFY_AUTH_TOKEN`, the ordered load rule, no-login).
- [`references/cli-reference.md`](references/cli-reference.md) — the `netlify` CLI surface + the `netlify api` escape hatch.
- [`references/rest-api.md`](references/rest-api.md) — the REST long tail, the digest-deploy protocol, state + limits.
- This is the CLI-first sibling of `github-cli-ops` and the OpenAPI-grounded sibling of `atlassian-rest-ops`, under the per-provider service-skill pattern.

## Progressive disclosure

Heavy content lives in subfolders, loaded only on demand:

- [`references/credentials.md`](references/credentials.md) — caller-injected token, the ordered load rule, the Bearer bridge, no-login. Load in Step 1.
- [`references/cli-reference.md`](references/cli-reference.md) — the CLI commands + escape hatch + CLI gotchas. Load in Steps 2–3.
- [`references/rest-api.md`](references/rest-api.md) — the REST pattern, priority-op table, digest-deploy protocol, state + limits. Load for the REST tail.
- [`references/sources.md`](references/sources.md) — provenance (official OpenAPI + CLI/API docs + the two source skills) + the "confirm live" items.
- `assets/cli-index.md` — the CLI quick command list (Step 2).
- `assets/endpoint-index.md` — one line per REST operation (Step 2).
- `assets/netlify-openapi.json` — the bundled spec (Swagger 2.0; queried via the resolver, never loaded wholesale).
- `scripts/endpoint.py` + `.validation.md` — the `python3` `$ref`-resolver (Step 2).
- `scripts/{create-site,deploy,set-custom-domain,deploy-status}.sh` + `.validation.md` — four validated priority-op scripts.

## Standalone usage (optional, not required)

This is a convenience for a **human running the skill by hand** outside an agent-flow — it is **not a dependency of the skill**. The skill's normative contract is caller-injection (Step 1); this appendix is only the manual-operator bridge.

To run by hand, create a Netlify PAT (User → Applications → Personal access tokens), store its value in a gitignored `.env`, install the CLI (`npm i -g netlify-cli`), then populate the var yourself:

```bash
set -a; source .env; set +a                 # loads $NETLIFY_PROD_TOKEN, never prints it
export NETLIFY_AUTH_TOKEN="$NETLIFY_PROD_TOKEN"
bash scripts/create-site.sh my-site
bash scripts/deploy.sh <site-id> ./dist --prod
```

The token value is referenced by name only, never printed. Prefer a revocable, short-lived PAT.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap).
- Body ≤ ~500 lines / 5,000 tokens — kept in context every turn; CLI/REST detail lives in `references/`.
- `assets/netlify-openapi.json` is large (queried on disk, never loaded into context).
