#!/usr/bin/env bash
# Fetch a build's full plaintext console log. Env: base_url, username, JENKINS_TOKEN.
# Args: <job-name> [build-number]   (default build = lastBuild)
# For streaming/incremental tailing use logText/progressiveText?start=<offset> instead.
set -euo pipefail
job="$1"; build="${2:-lastBuild}"
curl -sS -u "$username:$JENKINS_TOKEN" "$base_url/job/$job/$build/consoleText"
