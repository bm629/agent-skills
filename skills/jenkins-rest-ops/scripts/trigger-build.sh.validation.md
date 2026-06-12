# Validation: trigger-build.sh

- **Method**: syntax check (`bash -n`); path/method verified against `assets/endpoint-index.md` (official Remote Access API).
- **Tools**: `bash -n` (clean); shellcheck not installed — skipped; `awk` for the Location header.
- **Date**: 2026-06-12
- **Exit codes**: `bash -n`: 0.

## Captured output

`bash -n` clean. No-arg → `POST job/<name>/build`; with `K=V` args → `POST job/<name>/buildWithParameters --data K=V` (repeatable) — matches the official trigger endpoints. Extracts the `Location:` queue-item URL from the response headers (`-D -`), the async-correct result (a build POST returns a queue item, not a build).

## Caveats

- Not executed live (needs a real server + job) — Phase 2.D smoke (trigger → poll → status → console).
- Follows the OFFICIAL trigger path, not swaggy-jenkins' invented `json` query param.
- Token auth is crumb-exempt; on a `403 No valid crumb` add `-H "$(bash scripts/crumb.sh)"`.
