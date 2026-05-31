#!/usr/bin/env bash
# Create a GitHub issue (CLI path). Requires GH_TOKEN in env (see references/auth.md);
# GH_REPO=OWNER/REPO selects the repo (or pass it via gh's own --repo).
# Usage: GH_TOKEN=$TOK GH_REPO=OWNER/REPO bash create-issue.sh "<title>" "<body>" [label]
set -euo pipefail
: "${GH_TOKEN:?set GH_TOKEN — see references/auth.md}"
title="${1:?usage: create-issue.sh <title> <body> [label]}"
body="${2:?usage: create-issue.sh <title> <body> [label]}"
args=(issue create --title "$title" --body "$body")
[ -n "${3:-}" ] && args+=(--label "$3")
exec gh "${args[@]}"
