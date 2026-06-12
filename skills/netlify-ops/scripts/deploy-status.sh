#!/usr/bin/env bash
# Read a deploy's status (the `state` field: building/uploading/processing/ready/error).
# Env: NETLIFY_AUTH_TOKEN. Args: <site-id> <deploy-id>
# Uses the REST getSiteDeploy via the CLI escape hatch. Pure REST alternative:
#   curl -sS -H "Authorization: Bearer $NETLIFY_AUTH_TOKEN" \
#     "https://api.netlify.com/api/v1/sites/<site-id>/deploys/<deploy-id>"
set -euo pipefail
site_id="$1"; deploy_id="$2"
netlify api getSiteDeploy --data "$(jq -n --arg s "$site_id" --arg d "$deploy_id" \
  '{site_id:$s, deploy_id:$d}')"
