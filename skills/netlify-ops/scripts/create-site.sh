#!/usr/bin/env bash
# Create a Netlify site (CLI-first). Env: NETLIFY_AUTH_TOKEN. Args: <site-name> [account-slug]
# Prints the created site as JSON (incl. the opaque site_id used by every other op).
# REST fallback (pure curl, unambiguous body): curl -X POST .../api/v1/sites
#   -H "Authorization: Bearer $NETLIFY_AUTH_TOKEN" -d '{"name":"<name>"}'
set -euo pipefail
name="$1"; slug="${2:-}"
args=(sites:create --name "$name" --disable-linking --json)
[ -n "$slug" ] && args+=(--account-slug "$slug")
netlify "${args[@]}"
