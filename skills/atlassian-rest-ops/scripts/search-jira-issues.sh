#!/usr/bin/env bash
# Example: search Jira issues via the new JQL endpoint, following nextPageToken.
#   python3 scripts/endpoint.py jira searchAndReconsileIssuesUsingJql
# Env: ATLASSIAN_EMAIL, ATLASSIAN_API_TOKEN, ATLASSIAN_BASE_URL
# Args: [jql]   (default: issues created in the last 30 days)
# NOTE: /search/jql rejects UNBOUNDED JQL (ordering-only or empty) with 400 —
#       always include a search restriction (project=, created>=, assignee=, ...).
set -euo pipefail
jql="${1:-created >= -30d order by created DESC}"
token=""
while :; do
  q="jql=$(printf %s "$jql" | jq -sRr @uri)&maxResults=50&fields=summary"
  if [ -n "$token" ]; then q="$q&nextPageToken=$token"; fi
  resp="$(curl -sS -u "$ATLASSIAN_EMAIL:$ATLASSIAN_API_TOKEN" -H "Accept: application/json" \
          "$ATLASSIAN_BASE_URL/rest/api/3/search/jql?$q")"
  echo "$resp" | jq -r '.issues[]? | "\(.key)\t\(.fields.summary)"'
  token="$(echo "$resp" | jq -r '.nextPageToken // empty')"
  if [ -z "$token" ]; then break; fi
done
