# Validation: crumb.sh

- **Method**: syntax check (`bash -n`); behavior verified against the official crumbIssuer contract (`references/patterns.md`).
- **Tools**: `bash -n` (clean); shellcheck not installed — skipped; `jq` 1.8.1 present.
- **Date**: 2026-06-12
- **Exit codes**: `bash -n`: 0.

## Captured output

`bash -n` clean. GETs `crumbIssuer/api/json`, parses `crumbRequestField` (default `Jenkins-Crumb`) + `crumb` via `jq`, and prints `field:value` for use as a POST header. Exits 0 printing nothing when the endpoint 404s (CSRF disabled) or returns no crumb — the documented graceful path.

## Caveats

- A FALLBACK only: API-token Basic auth is crumb-exempt on Jenkins 2.96/2.107+, so this is needed only when a POST returns `403 No valid crumb`. Not executed live (needs a real server) — Phase 2.D smoke exercises the crumb path if the test server enforces CSRF.
