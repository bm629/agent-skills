#!/usr/bin/env bash
# Add a custom domain to a Pages project (REST — Wrangler has no command for this).
# Env: CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID. Args: <project-name> <domain>
# This POST only REGISTERS the domain (status=initializing); it does NOT create the
# DNS record — even on a same-account zone (only the dashboard auto-creates it).
# Validation stays pending ("CNAME record not set") until a CNAME <domain> ->
# <project>.pages.dev exists on the zone; a Pages-scoped token cannot create that
# record (needs Zone DNS:Edit) — the caller adds it out-of-band.
# Check the {success, errors, messages, result} envelope, not just the HTTP status.
set -euo pipefail
project="$1"; domain="$2"
curl -sS -X POST \
  "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/pages/projects/$project/domains" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg n "$domain" '{name:$n}')"
