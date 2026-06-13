#!/usr/bin/env bash
# Create a Netlify site (CLI-first). Env: NETLIFY_AUTH_TOKEN. Args: <site-name> [account-slug]
# Prints the created site as JSON. The id every other op keys on is the `id` field —
# `sites:create --json` returns it as `id`, NOT `site_id` (`.site_id` is null on create);
# pass that `id` value as `--site` to deploy. (deploy/status JSON do use `site_id`.)
# REST fallback (pure curl, unambiguous body): curl -X POST .../api/v1/sites
#   -H "Authorization: Bearer $NETLIFY_AUTH_TOKEN" -d '{"name":"<name>"}'
set -euo pipefail
name="$1"; slug="${2:-}"
args=(sites:create --name "$name" --disable-linking --json)
[ -n "$slug" ] && args+=(--account-slug "$slug")
netlify "${args[@]}"
