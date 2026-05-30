#!/usr/bin/env bash
# Example: create a Confluence page (storage body). Verified shape:
#   python3 scripts/endpoint.py confluence createPage
# Env: ATLASSIAN_EMAIL, ATLASSIAN_API_TOKEN, ATLASSIAN_BASE_URL (https://<site>.atlassian.net)
# Args: <space-id> <title> [storage-html]
# Note: jq is used to build JSON safely (optional; inline the JSON if jq is absent).
set -euo pipefail
space_id="$1"; title="$2"; html="${3:-<p>Created via REST.</p>}"
curl -sS -u "$ATLASSIAN_EMAIL:$ATLASSIAN_API_TOKEN" -X POST \
  -H "Accept: application/json" -H "Content-Type: application/json" \
  "$ATLASSIAN_BASE_URL/wiki/api/v2/pages" \
  -d "$(jq -n --arg s "$space_id" --arg t "$title" --arg v "$html" \
        '{spaceId:$s, status:"current", title:$t, body:{representation:"storage", value:$v}}')"
