#!/usr/bin/env bash
# List jobs at the root (name + url + color/status). Env: base_url, username, JENKINS_TOKEN.
# Uses ?tree= to keep the response small. For a nested folder, pass its path:
#   bash scripts/list-jobs.sh job/<folder>
# NOTE: -g/--globoff is REQUIRED — the ?tree=jobs[...] brackets are curl glob
# metacharacters, so without -g curl aborts with "bad range" (curl error 3).
set -euo pipefail
prefix="${1:-}"
base="$base_url${prefix:+/$prefix}"
curl -sSg -u "$username:$JENKINS_TOKEN" "$base/api/json?tree=jobs[name,url,color]"
