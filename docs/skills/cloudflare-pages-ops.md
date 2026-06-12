# cloudflare-pages-ops

> Drive Cloudflare Pages **CLI-first** (Wrangler) with a **REST fallback** on
> Cloudflare's official API — no SDK. Wrangler is the ergonomic common path
> (create a project, deploy a build directory); the REST API is the
> comprehensive long tail (custom domains, deployment status, project/
> deployment/domain management), grounded on a bundled **Pages slice** of
> Cloudflare's OpenAPI via an endpoint index + a `$ref`-resolver. Auth is a
> scoped `CLOUDFLARE_API_TOKEN` (Bearer) + a non-secret `CLOUDFLARE_ACCOUNT_ID`;
> it **never** runs `wrangler login`. It consumes **caller-injected**
> credentials and never prints the token.

**Skill file:** [`skills/cloudflare-pages-ops/SKILL.md`](../../skills/cloudflare-pages-ops/SKILL.md)
**Version:** 1.0.0

## Purpose

Gives an agent the Cloudflare Pages static/JAMstack + serverless surface —
create a project, deploy a build, add/list a custom domain, read deployment
status, and the adjacent projects/deployments/domains REST surface (every path
account-scoped under `/accounts/{account_id}/pages/...`). It is the CLI-first
sibling of `github-cli-ops` and the OpenAPI-grounded sibling of
`atlassian-rest-ops` / `netlify-ops`. Full-stack container/app hosting is out of
scope.

## The bundled Pages slice

Cloudflare's official OpenAPI is ~10 MB / ~1986 paths. The skill bundles only the
**Pages slice** — the 11 account-scoped `/pages/...` paths + their transitive
`$ref` closure (a self-contained ~100 KB slice, 0 dangling refs) — resolved one
op at a time via `scripts/endpoint.py`; the full spec is never fetched into
context.

## When to activate

- ✅ Creating a Pages project, or deploying a build directory (Direct Upload).
- ✅ Adding/listing a custom domain, or reading deployment status (the stage machine).
- ✅ Listing/inspecting/deleting projects, deployments (retry/rollback), or domains.

Not for: full-stack container hosting, credential setup, or `wrangler login`.

## Workflow

1. **Receive the injected credentials** — `account_id` (non-secret context) + the
   token by variable name; bridge into `CLOUDFLARE_ACCOUNT_ID` + `CLOUDFLARE_API_TOKEN`.
   Never `wrangler login`.
2. **Pick the path** — Wrangler (`assets/cli-index.md`) for create/deploy; REST
   (`assets/endpoint-index.md` + `scripts/endpoint.py`) for the tail.
3. **Run it** — the four scripts cover create-project / deploy / add-custom-domain /
   deployment-status.
4. **Handle the response** — deploys are staged (poll `latest_stage` until the
   `deploy` stage is `success`); check the `{success, errors, messages, result}`
   envelope, not just HTTP status.

## Key gotchas

- **Don't log in** — a missing token/account_id is a hard caller error.
- **`CLOUDFLARE_ACCOUNT_ID` is required headlessly** — the most common CI failure.
- **Deploy is multipart** — the REST `create-deployment` body is `multipart/form-data`;
  deploy a directory with `wrangler pages deploy`, never a hand-rolled curl.
- **Direct Upload vs Git-connected** — `wrangler pages deploy` is for Direct-Upload
  projects; a Git-connected project deploys on `git push`.
- **The envelope hides failures** — a `200` can carry `success:false`.
- **No Wrangler custom-domain command** — that is REST-only.

## Credential contract

Pure consumer of caller-injected credentials: `account_id` as **non-secret**
context (not pushed through the token-load rule), the token by variable NAME
(project `.env`-then-env-var, no scope-walk, no `.service-accounts.yaml`, no
`--account`, no login). The token value is read only by the Wrangler/`curl`
subprocess, never printed. A "Standalone usage" appendix documents the by-hand
bridge.
