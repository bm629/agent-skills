# Validation: deploy-status.sh

- **Method**: syntax check (`bash -n`); op verified against `python3 scripts/endpoint.py getSiteDeploy`.
- **Tools**: `bash -n` (clean); shellcheck not installed — skipped; `jq` 1.8.1 present.
- **Date**: 2026-06-12
- **Exit codes**: `bash -n`: 0.

## Captured output

`bash -n` clean. Calls `netlify api getSiteDeploy --data '{"site_id":...,"deploy_id":...}'` — `getSiteDeploy` is path-params-only, so the escape-hatch payload keys map unambiguously to `site_id`/`deploy_id` (the verified `netlify api <op> --data` pattern). Returns the deploy incl. the `state` field (building/uploading/processing/ready/error). The comment gives the pure-REST `curl` alternative.

## Caveats

- Not run live (needs `NETLIFY_AUTH_TOKEN` + a deploy) — Phase 2.D smoke.
- The `state` value set is from Netlify docs, not a spec enum (flagged in `sources.md`).
