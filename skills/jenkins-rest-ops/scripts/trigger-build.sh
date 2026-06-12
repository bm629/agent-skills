#!/usr/bin/env bash
# Trigger a build; print the queue-item URL from the Location header.
# Env: base_url, username, JENKINS_TOKEN.
# Args: <job-name> [PARAM=value ...]   (no params -> /build; params -> /buildWithParameters)
# The build is ASYNC — this returns a QUEUE ITEM, not a build. Poll it with poll-queue-item.sh.
set -euo pipefail
job="$1"; shift || true
if [ "$#" -eq 0 ]; then
  endpoint="job/$job/build"; data=()
else
  endpoint="job/$job/buildWithParameters"; data=()
  # --data-urlencode splits on the first '=' and encodes the value, so a value
  # with spaces or &/= (e.g. MESSAGE=hello world) is sent correctly.
  for kv in "$@"; do data+=(--data-urlencode "$kv"); done
fi
# Token Basic auth is crumb-exempt on current Jenkins; add a crumb only on a 403 (see crumb.sh).
loc="$(curl -sS -u "$username:$JENKINS_TOKEN" -X POST -D - -o /dev/null \
  "$base_url/$endpoint" "${data[@]}" | awk 'tolower($1)=="location:"{print $2}' | tr -d '\r')"
echo "${loc:-"(no Location header — check auth / job name / 403 crumb)"}"
