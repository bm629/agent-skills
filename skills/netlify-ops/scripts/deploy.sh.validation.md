# Validation: deploy.sh

- **Method**: syntax check (`bash -n`); flags verified against the official `netlify deploy` docs.
- **Tools**: `bash -n` (clean); shellcheck not installed — skipped. (CLI not installed locally.)
- **Date**: 2026-06-12
- **Exit codes**: `bash -n`: 0.

## Captured output

`bash -n` clean. Runs `netlify deploy --dir <dir> --site <site_id> --json [--prod]` — the verified deploy command. Default is a draft/preview deploy; `--prod` publishes to production. `--site` is always passed explicitly (a fresh CI checkout has no `.netlify/state.json`). The CLI wraps the digest upload protocol.

## Caveats

- Not run live (CLI not installed locally; needs `NETLIFY_AUTH_TOKEN` + a site) — Phase 2.D smoke.
- There is no `--build` flag (the CLI builds by default; `--no-build` opts out). Deploys are rate-limited (3/min, 100/day).
