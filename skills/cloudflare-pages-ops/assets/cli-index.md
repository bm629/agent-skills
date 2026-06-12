# Wrangler CLI index — the common path

The ergonomic common path for Cloudflare Pages is the **Wrangler** CLI (`wrangler`, npm `wrangler`). It runs headlessly when `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID` are set — **never** `wrangler login` (OAuth) in an agent flow.

## Auth (headless)

- Export `CLOUDFLARE_API_TOKEN` (the injected scoped token, by variable name) and `CLOUDFLARE_ACCOUNT_ID` (the injected `account_id`). Both are required for non-interactive use — a missing account id is the most common headless failure.
- No `wrangler login`. The token + account id are the only auth.

## Pages commands

| Need | Command | Key flags |
|---|---|---|
| Create a project | `wrangler pages project create <name> --production-branch <branch>` | `--compatibility-date`, `--compatibility-flags` |
| Deploy a build | `wrangler pages deploy <dir> --project-name <name>` | `--branch <name>`, `--commit-dirty <bool>`, `--commit-hash <sha>`, `--commit-message <msg>` |
| List projects | `wrangler pages project list` | `--json` |
| Delete a project | `wrangler pages project delete <name>` | `--yes` |
| List deployments | `wrangler pages deployment list --project-name <name>` | `--json`, `--environment` |
| Tail a deployment | `wrangler pages deployment tail <deployment>` | status/method/IP filters |

- `--json` is available on `project list` and `deployment list` — prefer it in scripts.
- **`wrangler pages deploy` is for Direct-Upload projects.** A Git-connected project deploys automatically on `git push`, not via Wrangler. (And a Direct-Upload project cannot later switch to Git integration.)
- **No Wrangler command adds a custom domain** — that is REST-only (`POST .../domains`, see `references/rest-api.md` and `scripts/add-custom-domain.sh`).
- `--commit-dirty true` lets a deploy proceed from an uncommitted working tree.

## The REST fallback

For project/deployment/domain **management** (and anything Wrangler doesn't cover), drop to the REST API — scan `assets/endpoint-index.md`, resolve with `python3 scripts/endpoint.py <operationId>`, then `curl`. See `references/rest-api.md`. Deploying a directory is **Wrangler's** job (the REST deploy is a multipart upload) — don't hand-roll it.
