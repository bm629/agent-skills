# Validation: list-jobs.sh

- **Method**: syntax check (`bash -n`); path verified against `assets/endpoint-index.md`.
- **Tools**: `bash -n` (clean); shellcheck not installed — skipped.
- **Date**: 2026-06-12
- **Exit codes**: `bash -n`: 0.

## Captured output

`bash -n` clean. GETs `api/json?tree=jobs[name,url,color]` at the root (or under an optional `job/<folder>` prefix for nested folders) — the `?tree=` filter avoids a huge response. `color` encodes job status (blue/red/disabled/…).

## Caveats

- Not executed live (needs a real server) — Phase 2.D smoke.
- For nested folders, pass the path with repeated `job/` segments, e.g. `job/myfolder`.
