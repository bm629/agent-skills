# Validation: search-jira-issues.sh

- **Method**: syntax check (`bash -n`); pagination shape verified against `python3 endpoint.py jira searchAndReconsileIssuesUsingJql`
- **Tools**: `bash -n`; shellcheck: not installed — skipped; jq 1.8.1 present
- **Date**: 2026-05-31
- **Exit codes**: `bash -n`: 0

## Captured output
`bash -n` clean. Uses the newer `/rest/api/3/search/jql` with `nextPageToken` pagination + URL-encoded JQL — matches the verified Jira token-pagination pattern.

## Caveats
- Validated live (2026-05-31): `/search/jql` returns 200 for a **bounded** JQL; an **unbounded** query (ordering-only/empty) → 400 `ErrorCollection`. Default JQL is bounded (`created >= -30d …`).
- Uses `jq` for URL-encoding the JQL + parsing results.
