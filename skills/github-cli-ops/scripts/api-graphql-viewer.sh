#!/usr/bin/env bash
# API fallback (GraphQL): read the authenticated viewer's login via gh api graphql.
# Usage: GH_TOKEN=$TOK bash api-graphql-viewer.sh
set -euo pipefail
: "${GH_TOKEN:?set GH_TOKEN — see references/auth.md}"
exec gh api graphql -f query='{ viewer { login } }'
