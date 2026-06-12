#!/usr/bin/env bash
# Create a Cloudflare Pages project (Wrangler — the common path).
# Env: CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID. Args: <project-name> [production-branch]
# Creates a Direct-Upload project (deploy with deploy.sh). REST fallback:
#   POST /accounts/$CLOUDFLARE_ACCOUNT_ID/pages/projects  {"name":"<n>","production_branch":"<b>"}
set -euo pipefail
name="$1"; branch="${2:-main}"
wrangler pages project create "$name" --production-branch "$branch"
