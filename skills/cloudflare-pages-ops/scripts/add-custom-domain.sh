#!/usr/bin/env bash
# Add a custom domain to a Pages project (REST — Wrangler has no command for this).
# Env: CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID. Args: <project-name> <domain>
# The domain must be on a Cloudflare zone with DNS pointed at the project.
# Check the {success, errors, messages, result} envelope, not just the HTTP status.
set -euo pipefail
project="$1"; domain="$2"
curl -sS -X POST \
  "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/pages/projects/$project/domains" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg n "$domain" '{name:$n}')"
