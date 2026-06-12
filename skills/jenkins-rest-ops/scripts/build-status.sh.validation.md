# Validation: build-status.sh

- **Method**: syntax check (`bash -n`); path verified against `assets/endpoint-index.md`.
- **Tools**: `bash -n` (clean); shellcheck not installed — skipped.
- **Date**: 2026-06-12
- **Exit codes**: `bash -n`: 0.

## Captured output

`bash -n` clean. GETs `job/<name>/<build>/api/json?tree=number,result,building,duration,timestamp,url` (default build `lastBuild`) — the `?tree=` filter keeps the response small. `result` is `null` while `building` is true.

## Caveats

- Not executed live (needs a real server + build) — Phase 2.D smoke.
