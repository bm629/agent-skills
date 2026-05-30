#!/usr/bin/env bash
# Example: create a Jira issue with an ADF description (RAW object). Verified shape:
#   python3 scripts/endpoint.py jira createIssue
# Env: ATLASSIAN_EMAIL, ATLASSIAN_API_TOKEN, ATLASSIAN_BASE_URL
# Args: <project-key> <summary> [issuetype=Task] [description-text]
set -euo pipefail
project_key="$1"; summary="$2"; issuetype="${3:-Task}"; text="${4:-Created via REST.}"
curl -sS -u "$ATLASSIAN_EMAIL:$ATLASSIAN_API_TOKEN" -X POST \
  -H "Accept: application/json" -H "Content-Type: application/json" \
  "$ATLASSIAN_BASE_URL/rest/api/3/issue" \
  -d "$(jq -n --arg p "$project_key" --arg it "$issuetype" --arg s "$summary" --arg t "$text" \
    '{fields:{project:{key:$p}, issuetype:{name:$it}, summary:$s,
       description:{version:1, type:"doc",
         content:[{type:"paragraph", content:[{type:"text", text:$t}]}]}}}')"
