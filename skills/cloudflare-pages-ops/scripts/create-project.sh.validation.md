# Validation: create-project.sh

- **Method**: syntax check (`bash -n`); command verified against the official Wrangler Pages docs (`assets/cli-index.md`).
- **Tools**: `bash -n` (clean); shellcheck not installed — skipped. (Wrangler is not installed locally — not run live.)
- **Date**: 2026-06-12
- **Exit codes**: `bash -n`: 0.

## Captured output

`bash -n` clean. Runs `wrangler pages project create <name> --production-branch <branch>` — the verified create command (creates a Direct-Upload project). Auth via `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID`. REST fallback (`POST .../pages/projects`, body `name`+`production_branch`) is in the comment.

## Caveats

- Not run live (Wrangler not installed locally; needs the token + account_id) — Phase 2.D smoke (create → deploy → status).
