#!/usr/bin/env bash
# Get a file by id (full document incl. data). Resolve: python3 scripts/endpoint.py get-file
# Env: base_url, PENPOT_TOKEN. Args: <file-uuid>
# Note the field is `id` here, but `fileId` on duplicate-file — match each command's schema.
# For metadata only (no heavy `data`), use get-file-summary / get-file-info instead.
set -euo pipefail
file_id="$1"
curl -sS -X POST "$base_url/api/rpc/command/get-file" \
  -H "Authorization: Token $PENPOT_TOKEN" \
  -H "Content-Type: application/json" -H "Accept: application/json" \
  -d "$(jq -n --arg i "$file_id" '{id:$i}')"
