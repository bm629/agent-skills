# Cloudflare Pages REST endpoint index

One line per operation: `METHOD path — summary (operationId)`. Base = `https://api.cloudflare.com/client/v4`; every path is prefixed with `/accounts/{account_id}` (shown trimmed below) and auth is `Authorization: Bearer <token>`. Find the operation, then run `python3 scripts/endpoint.py <operationId>` to resolve its params + body schema ($ref-resolved against the bundled Pages slice) + a curl skeleton. Responses use the Cloudflare envelope `{success, errors, messages, result}`. The bundled spec is the Pages-only slice of Cloudflare's official OpenAPI 3.0.3.

## Operations (20)

- `GET /pages/projects` — Get projects (`pages-project-get-projects`)
- `POST /pages/projects` — Create project (`pages-project-create-project`) body=application/json
- `DELETE /pages/projects/{project_name}` — Delete project (`pages-project-delete-project`)
- `GET /pages/projects/{project_name}` — Get project (`pages-project-get-project`)
- `PATCH /pages/projects/{project_name}` — Update project (`pages-project-update-project`) body=application/json
- `GET /pages/projects/{project_name}/deployments` — Get deployments (`pages-deployment-get-deployments`)
- `POST /pages/projects/{project_name}/deployments` — Create deployment (`pages-deployment-create-deployment`) body=multipart/form-data
- `DELETE /pages/projects/{project_name}/deployments/{deployment_id}` — Delete deployment (`pages-deployment-delete-deployment`)
- `GET /pages/projects/{project_name}/deployments/{deployment_id}` — Get deployment info (`pages-deployment-get-deployment-info`)
- `GET /pages/projects/{project_name}/deployments/{deployment_id}/history/logs` — Get deployment logs (`pages-deployment-get-deployment-logs`)
- `POST /pages/projects/{project_name}/deployments/{deployment_id}/retry` — Retry deployment (`pages-deployment-retry-deployment`)
- `POST /pages/projects/{project_name}/deployments/{deployment_id}/rollback` — Rollback deployment (`pages-deployment-rollback-deployment`)
- `GET /pages/projects/{project_name}/domains` — Get domains (`pages-domains-get-domains`)
- `POST /pages/projects/{project_name}/domains` — Add domain (`pages-domains-add-domain`) body=application/json
- `DELETE /pages/projects/{project_name}/domains/{domain_name}` — Delete domain (`pages-domains-delete-domain`)
- `GET /pages/projects/{project_name}/domains/{domain_name}` — Get domain (`pages-domains-get-domain`)
- `PATCH /pages/projects/{project_name}/domains/{domain_name}` — Patch domain (`pages-domains-patch-domain`)
- `POST /pages/projects/{project_name}/purge_build_cache` — Purge build cache (`pages-purge-build-cache`)
- `DELETE /pages/projects/{project_name}/source` — Disconnect project source (`pages-project-disconnect-project-source`)
- `POST /pages/projects/{project_name}/source` — Connect project source (`pages-project-connect-project-source`) body=application/json
