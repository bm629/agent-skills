# The Cloudflare Pages REST API — the long-tail fallback

The REST API is the comprehensive fallback under `https://api.cloudflare.com/client/v4`, auth `Authorization: Bearer <token>`. **Every** Pages path is account-scoped — `/accounts/{account_id}/pages/...`. Use it for project/deployment/domain management (Wrangler covers create + deploy). Scan `assets/endpoint-index.md`, resolve a shape with `python3 scripts/endpoint.py <operationId>`, then `curl`.

## The Cloudflare envelope — check `success`, not just HTTP

Every response is `{success, errors, messages, result}` (all four present). A `200` can still carry `success: false` — **always** test `success` and read `errors[].code` / `errors[].message` (e.g. `{"code":7003,"message":"No route for the URI"}`). `result` is `null` on failure.

## Priority + adjacent operations

| Need | operationId | Method + path (under `/accounts/{account_id}`) | Body |
|---|---|---|---|
| Create project | `pages-project-create-project` | POST `/pages/projects` | json `name`*, `production_branch`* (+ build_config, deployment_configs, source) |
| List projects | `pages-project-get-projects` | GET `/pages/projects` | — |
| Get project | `pages-project-get-project` | GET `/pages/projects/{project_name}` | — |
| Delete project | `pages-project-delete-project` | DELETE `/pages/projects/{project_name}` | — |
| Create deployment | `pages-deployment-create-deployment` | POST `/pages/projects/{project_name}/deployments` | **multipart/form-data** — use `wrangler pages deploy`, not curl |
| List deployments | `pages-deployment-get-deployments` | GET `/pages/projects/{project_name}/deployments` | — |
| Get deployment | `pages-deployment-get-deployment-info` | GET `/pages/projects/{project_name}/deployments/{deployment_id}` | → `latest_stage` |
| Retry deployment | `pages-deployment-retry-deployment` | POST `/.../deployments/{deployment_id}/retry` | (no body) |
| Rollback deployment | `pages-deployment-rollback-deployment` | POST `/.../deployments/{deployment_id}/rollback` | (no body) |
| Deployment logs | `pages-deployment-get-deployment-logs` | GET `/.../deployments/{deployment_id}/history/logs` | — |
| List domains | `pages-domains-get-domains` | GET `/pages/projects/{project_name}/domains` | — |
| Add domain | `pages-domains-add-domain` | POST `/pages/projects/{project_name}/domains` | json `name`* |
| Get / delete domain | `pages-domains-get-domain` / `…-delete-domain` | GET/DELETE `/.../domains/{domain_name}` | — |
| Purge build cache | `pages-purge-build-cache` | POST `/.../purge_build_cache` | — |

## Deploy status — the stage machine

A deployment carries `latest_stage` (and the full `stages` array). `latest_stage`:

- `name` ∈ `queued | initialize | clone_repo | build | deploy`
- `status` ∈ `success | idle | active | failure | canceled`

Poll `pages-deployment-get-deployment-info` until the `deploy` stage reaches `status: success` (done-good) or any stage hits `status: failure`. `scripts/deployment-status.sh` reads it.

## Deploy is multipart — use Wrangler

The REST `create-deployment` body is `multipart/form-data` (binary file parts), so a directory deploy over raw `curl` is impractical. **Deploy with `wrangler pages deploy <dir>`**; reserve REST for management ops.

## Limits

- Global Cloudflare API limit: **1,200 requests / 5 minutes per user** (cumulative across dashboard/key/token); over-limit → HTTP 429 for the next 5 minutes. Some endpoints are tighter.
