#!/usr/bin/env bash
# Print the CSRF crumb header line "Jenkins-Crumb:<value>" for a POST FALLBACK.
# With API-token Basic auth the crumb is EXEMPT (Jenkins 2.96/2.107+), so you
# normally do NOT need this — only call it if a POST returns 403 "No valid crumb".
# If CSRF is disabled the crumb endpoint 404s; this prints nothing and exits 0.
# Env: base_url, username, JENKINS_TOKEN.  Usage: hdr="$(bash scripts/crumb.sh)"
set -uo pipefail
body="$(curl -sS -u "$username:$JENKINS_TOKEN" "$base_url/crumbIssuer/api/json" 2>/dev/null)" || exit 0
[ -z "$body" ] && exit 0
field="$(printf '%s' "$body" | jq -r '.crumbRequestField // "Jenkins-Crumb"' 2>/dev/null)"
value="$(printf '%s' "$body" | jq -r '.crumb // empty' 2>/dev/null)"
[ -z "$value" ] && exit 0
printf '%s:%s' "$field" "$value"
