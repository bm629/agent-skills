# Validation: get-projects.sh

- **Method**: syntax check (`bash -n`); body shape verified against `python3 scripts/endpoint.py get-projects`.
- **Tools**: `bash -n` (clean); shellcheck not installed — skipped; `jq` 1.8.1 present (builds the JSON body safely).
- **Date**: 2026-06-12
- **Exit codes**: `bash -n`: 0.

## Captured output

`bash -n` clean. Builds `{teamId}` via `jq` and POSTs to `/api/rpc/command/get-projects` — matches the resolved schema (`teamId` required). The doc notes `get-all-projects` (no team-id) for the cross-team list.

## Caveats

- Not executed live (needs a real base_url + token + team UUID) — Phase 2.D smoke.
- Requires `jq`; inline the JSON if `jq` is absent.
