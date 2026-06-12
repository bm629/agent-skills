#!/usr/bin/env bash
# Verify-auth / whoami. The cheapest call to confirm the injected token works.
# Resolve the shape: python3 scripts/endpoint.py get-profile
# Env: base_url (e.g. https://design.penpot.app), PENPOT_TOKEN (the var name the
#      caller injected — referenced by name only, read here by curl, never printed).
# Returns the Profile, incl. defaultTeamId / defaultProjectId (handy seeds for other ops).
set -euo pipefail
curl -sS -X POST "$base_url/api/rpc/command/get-profile" \
  -H "Authorization: Token $PENPOT_TOKEN" \
  -H "Content-Type: application/json" -H "Accept: application/json" \
  -d '{}'
