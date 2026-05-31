#!/usr/bin/env bash
# View a repo as JSON (CLI path, structured output).
# Usage: GH_TOKEN=$TOK bash view-repo.sh OWNER/REPO
set -euo pipefail
: "${GH_TOKEN:?set GH_TOKEN — see references/auth.md}"
repo="${1:?usage: view-repo.sh OWNER/REPO}"
exec gh repo view "$repo" --json name,visibility,defaultBranchRef,description
