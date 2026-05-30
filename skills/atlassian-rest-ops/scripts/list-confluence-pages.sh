#!/usr/bin/env bash
# Example: list Confluence pages, following cursor pagination (_links.next).
#   python3 scripts/endpoint.py confluence getPages
# Env: ATLASSIAN_EMAIL, ATLASSIAN_API_TOKEN, ATLASSIAN_BASE_URL
set -euo pipefail
url="$ATLASSIAN_BASE_URL/wiki/api/v2/pages?limit=25"
while [ -n "$url" ]; do
  resp="$(curl -sS -u "$ATLASSIAN_EMAIL:$ATLASSIAN_API_TOKEN" -H "Accept: application/json" "$url")"
  echo "$resp" | jq -r '.results[]? | "\(.id)\t\(.title)"'
  # _links.next is a site-relative path (e.g. /wiki/api/v2/pages?cursor=...); prefix the host.
  next="$(echo "$resp" | jq -r '._links.next // empty')"
  if [ -n "$next" ]; then url="$ATLASSIAN_BASE_URL$next"; else url=""; fi
done
