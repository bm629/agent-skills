# Wrangler — the common path

Wrangler (npm `wrangler`) is the ergonomic common path for Cloudflare Pages. It runs headlessly when `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID` are set — **never** `wrangler login`. See `assets/cli-index.md` for the quick command list.

## Non-interactive rules

- Export `CLOUDFLARE_API_TOKEN` (the injected scoped token) + `CLOUDFLARE_ACCOUNT_ID` (the injected `account_id`). **Both** are required headlessly — a missing account id is the most common CI failure.
- `--json` on `project list` / `deployment list` for machine output.
- `wrangler pages deploy` is for **Direct-Upload** projects. A **Git-connected** project deploys automatically on `git push` — Wrangler will not deploy it. (And a Direct-Upload project cannot later switch to Git integration.)

## Commands

| Need | Command |
|---|---|
| Create a project | `wrangler pages project create <name> --production-branch <branch>` |
| Deploy a build | `wrangler pages deploy <dir> --project-name <name> [--branch <b>] --commit-dirty true` |
| List projects | `wrangler pages project list --json` |
| Delete a project | `wrangler pages project delete <name> --yes` |
| List deployments | `wrangler pages deployment list --project-name <name> --json` |
| Tail a deployment | `wrangler pages deployment tail <deployment>` |

## What Wrangler does NOT do (→ REST)

- **Custom domains** — there is no `wrangler pages domain` command; add/list/delete a custom domain via REST (`references/rest-api.md`, `scripts/add-custom-domain.sh`).
- **Deployment status by id** — read it via REST `pages-deployment-get-deployment-info` (`scripts/deployment-status.sh`); `deployment list` shows recent deployments but the per-deployment `latest_stage` is a REST read.

## Gotchas

- `--commit-dirty true` lets a deploy proceed from an uncommitted working tree (otherwise Wrangler flags it).
- The build directory passed to `pages deploy` is the **already-built** output (`dist`, `build`, `.output/public`, …) — Wrangler uploads it; it does not run your framework build.
- Deploy is **Direct-Upload only**; never try to `wrangler pages deploy` a Git-connected project.
