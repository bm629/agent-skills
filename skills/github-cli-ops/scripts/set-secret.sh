#!/usr/bin/env bash
# Set a repository secret (gh encrypts the value client-side before sending).
# Usage: GH_TOKEN=$TOK bash set-secret.sh OWNER/REPO SECRET_NAME SECRET_VALUE
set -euo pipefail
: "${GH_TOKEN:?set GH_TOKEN — see references/auth.md}"
repo="${1:?usage: set-secret.sh OWNER/REPO SECRET_NAME SECRET_VALUE}"
name="${2:?usage: set-secret.sh OWNER/REPO SECRET_NAME SECRET_VALUE}"
value="${3:?usage: set-secret.sh OWNER/REPO SECRET_NAME SECRET_VALUE}"
exec gh secret set "$name" --repo "$repo" --body "$value"
