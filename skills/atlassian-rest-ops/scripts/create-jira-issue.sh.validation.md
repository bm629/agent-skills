# Validation: create-jira-issue.sh

- **Method**: syntax check (`bash -n`); ADF body shape verified against `python3 endpoint.py jira createIssue`
- **Tools**: `bash -n`; shellcheck: not installed — skipped; jq 1.8.1 present
- **Date**: 2026-05-31
- **Exit codes**: `bash -n`: 0

## Captured output
`bash -n` clean. Builds `fields.description` as a **raw ADF object** (`{version:1,type:"doc",content:[paragraph→text]}`) — matches the verified Jira ADF pattern; POSTs to `/rest/api/3/issue`.

## Caveats
- Not executed live (needs a real account + project) — covered by the 2.D smoke test.
- `fields` requirements vary per project/screen; resolve with `endpoint.py` for a specific project. Uses `jq`.
