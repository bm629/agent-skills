#!/usr/bin/env bash
# Read a deployment's status (REST). Env: CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID.
# Args: <project-name> <deployment-id>
# Returns the deployment; poll .result.latest_stage.{name,status} — the deploy is
# done-good when the `deploy` stage reaches status `success`, failed on `failure`.
# Check the {success, errors, messages, result} envelope, not just the HTTP status.
set -euo pipefail
project="$1"; deploy_id="$2"
curl -sS \
  "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/pages/projects/$project/deployments/$deploy_id" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN"
