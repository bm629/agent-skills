# Validation: deploy.sh

- **Method**: syntax check (`bash -n`); command verified against the official Wrangler Pages docs.
- **Tools**: `bash -n` (clean); shellcheck not installed — skipped. (Wrangler not installed locally.)
- **Date**: 2026-06-12
- **Exit codes**: `bash -n`: 0.

## Captured output

`bash -n` clean. Runs `wrangler pages deploy <dir> --project-name <name> --commit-dirty true [--branch <b>]` — the verified deploy command (wraps the multipart asset upload). For Direct-Upload projects only.

## Caveats

- Not run live (needs Wrangler + token + account_id) — Phase 2.D smoke.
- A Git-connected project deploys on `git push`, not via this command. The REST deploy endpoint is `multipart/form-data` — never hand-roll a directory deploy over curl.
