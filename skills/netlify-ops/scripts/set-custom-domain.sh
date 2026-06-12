#!/usr/bin/env bash
# Set a site's custom domain via the REST updateSite (PATCH) — the unambiguous path.
# Env: NETLIFY_AUTH_TOKEN. Args: <site-id> <domain>
# Verify afterward: curl ... GET /sites/<site-id> and check .custom_domain; then configure
# DNS (configureDNSForSite / dns_zones records) so the domain resolves.
set -euo pipefail
site_id="$1"; domain="$2"
curl -sS -X PATCH "https://api.netlify.com/api/v1/sites/$site_id" \
  -H "Authorization: Bearer $NETLIFY_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg d "$domain" '{custom_domain:$d}')"
