#!/usr/bin/env bash
# Read a build's status. Env: base_url, username, JENKINS_TOKEN.
# Args: <job-name> [build-number]   (default build = lastBuild)
# Prints result / building / duration. `result` is null while still building.
set -euo pipefail
job="$1"; build="${2:-lastBuild}"
curl -sS -u "$username:$JENKINS_TOKEN" \
  "$base_url/job/$job/$build/api/json?tree=number,result,building,duration,timestamp,url"
