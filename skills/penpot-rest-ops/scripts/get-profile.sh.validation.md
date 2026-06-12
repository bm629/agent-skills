# Validation: get-profile.sh

- **Method**: syntax check (`bash -n`); body shape verified against `python3 scripts/endpoint.py get-profile`.
- **Tools**: `bash -n` (clean); shellcheck not installed — skipped. No `jq` needed (empty `{}` body).
- **Date**: 2026-06-12
- **Exit codes**: `bash -n`: 0.

## Captured output

`bash -n` clean. POSTs `{}` to `/api/rpc/command/get-profile` with `Authorization: Token` + `Accept: application/json` — matches the resolved (no-field) schema and the official integration-guide whoami example.

## Caveats

- Not executed live (needs a real base_url + token) — the live create→read→list→cleanup smoke is the Phase 2.D step.
