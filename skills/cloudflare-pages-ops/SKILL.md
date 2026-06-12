---
# ─── UNIVERSAL CORE ──────────────────────────────────────────────────────
name: cloudflare-pages-ops
description: >
  Use when driving Cloudflare Pages web-hosting directly — creating a Pages
  project, deploying a build, adding a custom domain, reading deployment
  status, and listing/inspecting projects/deployments/domains. CLI-first on
  the Wrangler CLI (which reads CLOUDFLARE_API_TOKEN + CLOUDFLARE_ACCOUNT_ID
  and runs headlessly — never `wrangler login`) with a REST fallback on
  Cloudflare's official API at https://api.cloudflare.com/client/v4 (auth
  Authorization: Bearer <scoped token>; every path account-scoped under
  /accounts/{account_id}/pages/...). Resolves the Pages REST operations from a
  bundled OpenAPI slice via an endpoint index + a $ref-resolver, with the
  response envelope, deploy stage machine, and multipart-deploy +
  Direct-Upload-vs-Git caveats handled explicitly. Consumes caller-injected
  credentials (account_id from context + a token by variable name) — it does
  not provision them; the token is read only by the Wrangler/curl subprocess,
  never printed. Static/JAMstack + serverless, not full-stack container apps.

# ─── PROVIDER-SPECIFIC EXTENSIONS ────────────────────────────────────────
extensions:
  claude:
    allowed-tools: [Read, Write, Edit, Grep, Glob, Bash]
    user-invocable: true
    when_to_use: "performing a Cloudflare Pages operation (project/deploy/domain) via Wrangler or the REST API"
    argument-hint: "<operation, e.g. 'deploy ./dist to Pages project X'>"
  copilot: {}
  cursor:
    alwaysApply: false
    globs: []
  gemini: {}
  codex: {}

version: "1.0.0"

forge:
  status: unreviewed
  forged: 2026-06-12
  reviewed: null
---

# cloudflare-pages-ops

## Overview

This skill lets an agent perform Cloudflare Pages operations **CLI-first** (the Wrangler CLI) with a **REST fallback** on Cloudflare's official API — no SDK. Wrangler is the ergonomic common path (create a project, deploy a build directory); the REST API is the comprehensive long tail (custom domains, deployment status, project/deployment/domain management), grounded on a bundled Pages OpenAPI slice via an endpoint index + a `$ref`-resolver so coverage never loads the spec into context. The agent consumes the caller-injected `account_id` + token, picks the Wrangler command or REST operation, runs it, and parses the result. It drives Cloudflare Pages' static/JAMstack + serverless surface — not full-stack container hosting.

## When to activate

- ✅ Creating a Pages **project**, or deploying a build directory to one (Direct Upload).
- ✅ Adding/listing a **custom domain**, or reading **deployment status** (the stage machine).
- ✅ Listing/inspecting/deleting **projects**, **deployments** (retry/rollback), or **domains**.

**Do NOT activate when:**

- You need **full-stack container/app hosting** (Render, Fly.io, Railway, Vercel SSR-as-PaaS) — Cloudflare Pages here is a static/JAMstack + serverless host only.
- You only need credential setup — credentials are provided by the caller; this skill does not provision or resolve them, and never runs `wrangler login` (see `references/credentials.md`).

## Workflow

### Step 1 — Receive the injected credentials

The caller has already resolved the account and injected what this operation needs — **consume** it; do **not** look for a record or log in. You receive from context:

- **`account_id`** (a **non-secret** plain context value — exported as `CLOUDFLARE_ACCOUNT_ID` and interpolated into the REST path) and the **capability** (`web-hosting`).
- **The token, by an ordered load rule** the context carries the **variable NAME** for: the project-level **`.env` value if that file exists** and defines the var, **else** the **environment variable** of that name (project `.env` first). The token **value** is never in context prose — only its variable name. Perform **no** scope resolution or directory walk; it is project `.env`, not `.envrc`.

Bridge into `CLOUDFLARE_API_TOKEN` (Bearer) + `CLOUDFLARE_ACCOUNT_ID`. Never `wrangler login`. Full contract: [`references/credentials.md`](references/credentials.md).

### Step 2 — Pick the common path (Wrangler) or the long tail (REST)

- **Wrangler (common path):** scan [`assets/cli-index.md`](assets/) for `pages project create`, `pages deploy`, `pages project list`, `pages deployment list/tail`. Detail: [`references/wrangler.md`](references/wrangler.md).
- **REST (long tail):** scan [`assets/endpoint-index.md`](assets/), then `python3 scripts/endpoint.py <operationId>` to resolve params + body + a curl skeleton. Detail: [`references/rest-api.md`](references/rest-api.md). Never load the bundled slice into context.

### Step 3 — Run it

The four bundled scripts cover the priority ops:

- `create-project.sh <name> [branch]` — `wrangler pages project create … --production-branch …` (Direct-Upload project).
- `deploy.sh <project> <dir> [branch]` — `wrangler pages deploy … --commit-dirty true` (uploads the built dir).
- `add-custom-domain.sh <project> <domain>` — REST `POST …/domains` (Wrangler has no domain command).
- `deployment-status.sh <project> <deployment-id>` — REST `get-deployment-info` (the stage machine).

For anything else: Wrangler command from `cli-index.md`, or a `curl` against the resolved REST op.

### Step 4 — Handle the response

- **Deploys are async + staged.** A deployment moves through `latest_stage.name` ∈ queued/initialize/clone_repo/build/deploy with `status` ∈ success/idle/active/failure/canceled. Poll `deployment-status.sh` until the `deploy` stage reaches `status: success` (done) or any stage hits `failure`.
- **Check the envelope, not just HTTP.** Every REST response is `{success, errors, messages, result}` — a `200` can carry `success: false`; read `errors[].code/message`.
- **Custom domain ≠ DNS.** Adding a domain needs it on a Cloudflare zone with DNS pointed at the project.
- **Limits:** 1,200 requests / 5 min per user → HTTP 429.

## Rules

**Hard rules (never violate):**

- **Never `wrangler login`.** Auth is the injected `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID`; Wrangler runs headlessly. A missing token/account_id is a hard caller error, not a cue to log in.
- **Never read or print the token value.** Reference it only as `$CLOUDFLARE_API_TOKEN` (env / `Bearer`); the subprocess reads it from the environment. The token lives only in `.env` (gitignored) or the environment. `account_id` is non-secret context, not a secret.
- **Deploy a directory with Wrangler, not curl.** The REST `create-deployment` body is `multipart/form-data`; never hand-roll a directory deploy over `curl`.
- **Resolve before constructing a REST call.** Build a body/params from the `$ref`-resolved schema (`endpoint.py`) — never from a guessed field set.
- **Check `success`, not just HTTP.** A `200` with `success:false` is a failure — read `errors[]`.
- **This skill never writes credentials.** Credentials are provided by the caller.

**Preferences (override-able):**

- Pass `--json` to `wrangler pages project list` / `deployment list` for machine output.
- `--commit-dirty true` on a deploy from an uncommitted tree.
- Use REST for custom domains + per-deployment status (Wrangler has no command for those).

## Gotchas

- **Don't log in.** Reaching for `wrangler login` when the token "isn't working" violates the contract — a bad token/account_id is an error to surface, not a login to perform.
- **`CLOUDFLARE_ACCOUNT_ID` is required headlessly.** Wrangler needs it alongside the token; a missing account id is the most common CI failure.
- **Deploy is multipart.** The REST deploy endpoint is `multipart/form-data` (binary parts) — use `wrangler pages deploy <dir>`; don't JSON-POST a deploy.
- **Direct Upload vs Git-connected.** `wrangler pages deploy` works on **Direct-Upload** projects; a **Git-connected** project deploys on `git push` and Wrangler won't deploy it. (A Direct-Upload project can't later switch to Git.)
- **The envelope hides failures.** `{success:false}` can ride a `200`; always check it.
- **Custom domain needs DNS.** `add-custom-domain.sh` registers the domain; it only serves once DNS on a Cloudflare zone points at the project.
- **`pages deploy <dir>` uploads, doesn't build.** Pass the already-built output dir (`dist`/`build`/…); Wrangler doesn't run your framework build.
- **Rate limit.** 1,200 req/5 min per user, cumulative — back off on 429.

## Anti-patterns

- **Running `wrangler login`.** Forbidden — the contract injects the token; never resolve your own auth or prompt the user to log in.
- **Echoing the token.** Never `echo $CLOUDFLARE_API_TOKEN`, never paste it into a printed command, never write its value to a file. Reference the env var only. (`account_id` is non-secret and may appear in paths.)
- **Hand-rolling a directory deploy over REST.** The deploy is multipart — use Wrangler.
- **Guessing a REST body.** Resolve `create-project` / `add-domain` with `endpoint.py` — don't hand-write a body from memory.
- **Trusting the HTTP status alone.** A `200` with `success:false` is a failure — read `errors[]`.
- **Loading the whole spec.** Don't `cat` the bundled slice — scan the index, resolve one op. (And never fetch the 10 MB full Cloudflare OpenAPI.)

## Output

This skill produces **CLI/API side effects** (the requested Cloudflare Pages operation) and returns the parsed result to the calling agent. It writes no files of its own (it only *consumes* the caller-injected credentials). For a deploy it reports the deployment id + URL + terminal stage status; for a project it reports the project name/id + URL; for reads it returns the requested `result`. The abstract consumer is the calling agent (or a sub-agent) that needs the web-hosting operation performed; secrets never enter that output.

## Related

- [`references/credentials.md`](references/credentials.md) — the credential contract (`account_id` from context + token-by-name → `CLOUDFLARE_API_TOKEN`, the ordered load rule, no-login).
- [`references/wrangler.md`](references/wrangler.md) — the Wrangler Pages surface + what it doesn't cover.
- [`references/rest-api.md`](references/rest-api.md) — the REST long tail, the envelope, the deploy stage machine, limits.
- This is the CLI-first sibling of `github-cli-ops` and the OpenAPI-grounded sibling of `atlassian-rest-ops` / `netlify-ops`, under the per-provider service-skill pattern.

## Progressive disclosure

Heavy content lives in subfolders, loaded only on demand:

- [`references/credentials.md`](references/credentials.md) — caller-injected `account_id` + token, the ordered load rule, the Bearer bridge, no-login. Load in Step 1.
- [`references/wrangler.md`](references/wrangler.md) — the Wrangler commands + the Direct-Upload-vs-Git rule + CLI gotchas. Load in Steps 2–3.
- [`references/rest-api.md`](references/rest-api.md) — the REST pattern, the priority-op table, the envelope, the deploy stage machine, limits. Load for the REST tail.
- [`references/sources.md`](references/sources.md) — provenance (the bundled Pages slice + official docs) + the "confirm live" items.
- `assets/cli-index.md` — the Wrangler quick command list (Step 2).
- `assets/endpoint-index.md` — one line per REST operation (Step 2).
- `assets/cloudflare-pages-openapi.json` — the bundled Pages OpenAPI slice (queried via the resolver, never loaded wholesale).
- `scripts/endpoint.py` + `.validation.md` — the `python3` `$ref`-resolver (Step 2).
- `scripts/{create-project,deploy,add-custom-domain,deployment-status}.sh` + `.validation.md` — four validated priority-op scripts.

## Standalone usage (optional, not required)

This is a convenience for a **human running the skill by hand** outside an agent-flow — it is **not a dependency of the skill**. The skill's normative contract is caller-injection (Step 1); this appendix is only the manual-operator bridge.

To run by hand, create a scoped token (My Profile → API Tokens → Create Token, **Cloudflare Pages: Edit**), store its value in a gitignored `.env`, install Wrangler (`npm i -g wrangler`), then populate the vars yourself:

```bash
set -a; source .env; set +a                 # loads $CLOUDFLARE_PAGES_TOKEN, never prints it
export CLOUDFLARE_ACCOUNT_ID="<account-id>"
export CLOUDFLARE_API_TOKEN="$CLOUDFLARE_PAGES_TOKEN"
bash scripts/create-project.sh my-site main
bash scripts/deploy.sh my-site ./dist
```

The token value is referenced by name only, never printed. Prefer a revocable, short-lived scoped token.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap).
- Body ≤ ~500 lines / 5,000 tokens — kept in context every turn; Wrangler/REST detail lives in `references/`.
- `assets/cloudflare-pages-openapi.json` is the Pages slice (queried on disk, never loaded into context).
