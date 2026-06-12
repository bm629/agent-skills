#!/usr/bin/env bash
# Deploy a build directory to a Pages project (Wrangler — wraps the multipart upload).
# Env: CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID. Args: <project-name> <dir> [branch]
# Only for Direct-Upload projects (a Git-connected project deploys on git push).
# --commit-dirty true so a deploy from an uncommitted tree is not refused.
set -euo pipefail
project="$1"; dir="$2"; branch="${3:-}"
args=(pages deploy "$dir" --project-name "$project" --commit-dirty true)
[ -n "$branch" ] && args+=(--branch "$branch")
wrangler "${args[@]}"
