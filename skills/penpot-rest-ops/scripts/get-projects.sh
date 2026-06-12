#!/usr/bin/env bash
# List the projects in a team. Resolve: python3 scripts/endpoint.py get-projects
# Env: base_url, PENPOT_TOKEN. Args: <team-uuid>
# (For every project across all teams with no team-id, call get-all-projects instead.)
set -euo pipefail
team_id="$1"
curl -sS -X POST "$base_url/api/rpc/command/get-projects" \
  -H "Authorization: Token $PENPOT_TOKEN" \
  -H "Content-Type: application/json" -H "Accept: application/json" \
  -d "$(jq -n --arg t "$team_id" '{teamId:$t}')"
