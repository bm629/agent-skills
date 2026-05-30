# Validation: list-confluence-pages.sh

- **Method**: syntax check (`bash -n`); pagination shape verified against `python3 endpoint.py confluence getPages`
- **Tools**: `bash -n`; shellcheck: not installed — skipped; jq 1.8.1 present
- **Date**: 2026-05-31
- **Exit codes**: `bash -n`: 0

## Captured output
`bash -n` clean. Uses `limit` + cursor pagination, following `_links.next` (host-prefixed) until absent — matches the verified Confluence cursor pattern.

## Caveats
- Not executed live (needs a real account) — covered by the 2.D smoke test.
- `_links.next` is site-relative; the script prefixes `$ATLASSIAN_BASE_URL`. Uses `jq`.
