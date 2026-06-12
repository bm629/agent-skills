# Validation: create-file.sh

- **Method**: syntax check (`bash -n`); body shape verified against `python3 scripts/endpoint.py create-file`.
- **Tools**: `bash -n` (clean); shellcheck not installed — skipped; `jq` 1.8.1 present.
- **Date**: 2026-06-12
- **Exit codes**: `bash -n`: 0.

## Captured output

`bash -n` clean. Builds `{name, projectId}` via `jq` and POSTs to `/api/rpc/command/create-file` — matches the resolved schema (`name` + `projectId` required; `id`/`isShared`/`features` optional).

## Caveats

- Not executed live (needs a real base_url + token + project UUID) — Phase 2.D smoke (create→get→delete).
- Requires `jq`; inline the JSON if `jq` is absent.
