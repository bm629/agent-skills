#!/usr/bin/env bash
# Create a design file in a project. Resolve: python3 scripts/endpoint.py create-file
# Env: base_url, PENPOT_TOKEN. Args: <project-uuid> <file-name>
# Returns the created file (id, name, revn, projectId, …).
set -euo pipefail
project_id="$1"; name="$2"
curl -sS -X POST "$base_url/api/rpc/command/create-file" \
  -H "Authorization: Token $PENPOT_TOKEN" \
  -H "Content-Type: application/json" -H "Accept: application/json" \
  -d "$(jq -n --arg p "$project_id" --arg n "$name" '{name:$n, projectId:$p}')"
