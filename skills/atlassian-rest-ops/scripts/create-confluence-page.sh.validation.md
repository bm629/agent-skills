# Validation: create-confluence-page.sh

- **Method**: syntax check (`bash -n`); body shape verified against `python3 endpoint.py confluence createPage`
- **Tools**: `bash -n`; shellcheck: not installed — skipped; jq 1.8.1 present
- **Date**: 2026-05-31
- **Exit codes**: `bash -n`: 0

## Captured output
`bash -n` clean. Body `{spaceId, status:"current", title, body:{representation:"storage", value}}` matches the resolved `createPage` schema; POSTs to `/wiki/api/v2/pages`.

## Caveats
- Not executed live (needs a real account + space) — live create→verify→delete is the Phase 2.D smoke test.
- Uses `jq` to build JSON safely (present here; inline the JSON if `jq` is absent).
