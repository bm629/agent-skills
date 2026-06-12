# Validation: get-file.sh

- **Method**: syntax check (`bash -n`); body shape verified against `python3 scripts/endpoint.py get-file`.
- **Tools**: `bash -n` (clean); shellcheck not installed — skipped; `jq` 1.8.1 present.
- **Date**: 2026-06-12
- **Exit codes**: `bash -n`: 0.

## Captured output

`bash -n` clean. Builds `{id}` via `jq` and POSTs to `/api/rpc/command/get-file` — matches the resolved schema (`id` required; `features` optional). The script comment flags the `id`-vs-`fileId` naming difference (duplicate-file uses `fileId`) and the lighter `get-file-summary`/`get-file-info` variants.

## Caveats

- Not executed live (needs a real base_url + token + file UUID) — Phase 2.D smoke.
- Requires `jq`; inline the JSON if `jq` is absent.
