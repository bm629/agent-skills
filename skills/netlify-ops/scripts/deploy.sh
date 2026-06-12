#!/usr/bin/env bash
# Deploy a directory to a site (CLI-first — wraps the digest upload protocol).
# Env: NETLIFY_AUTH_TOKEN. Args: <site-id> <dir> [--prod]
# Default is a DRAFT/preview deploy (unique URL); pass --prod to publish to production.
# Always passes --site explicitly (a fresh CI checkout has no .netlify/state.json).
set -euo pipefail
site_id="$1"; dir="$2"; prod="${3:-}"
args=(deploy --dir "$dir" --site "$site_id" --json)
[ "$prod" = "--prod" ] && args+=(--prod)
netlify "${args[@]}"
