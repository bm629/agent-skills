#!/usr/bin/env bash
# API fallback: repo traffic views — no first-class gh command exists for this.
# Usage: GH_TOKEN=$TOK bash api-traffic-views.sh OWNER REPO
set -euo pipefail
: "${GH_TOKEN:?set GH_TOKEN — see references/auth.md}"
owner="${1:?usage: api-traffic-views.sh OWNER REPO}"
repo="${2:?usage: api-traffic-views.sh OWNER REPO}"
exec gh api "repos/$owner/$repo/traffic/views"
