#!/usr/bin/env bash
# Poll a queue item until it becomes an executable build; print the build URL + number.
# Env: base_url, username, JENKINS_TOKEN.
# Args: <queue-item-url>  (the Location from trigger-build.sh, e.g. $base_url/queue/item/42/)
# The queue item is ephemeral (~5 min after the build ends) — poll promptly.
set -euo pipefail
qurl="${1%/}"
for _ in $(seq 1 60); do
  j="$(curl -sS -u "$username:$JENKINS_TOKEN" "$qurl/api/json")"
  if printf '%s' "$j" | jq -e '.cancelled == true' >/dev/null 2>&1; then
    echo "cancelled"; exit 1
  fi
  num="$(printf '%s' "$j" | jq -r '.executable.number // empty')"
  if [ -n "$num" ]; then
    printf '%s\n' "$(printf '%s' "$j" | jq -r '.executable.url')"
    echo "build_number=$num"
    exit 0
  fi
  why="$(printf '%s' "$j" | jq -r '.why // "starting"')"
  echo "waiting: $why" >&2
  sleep 3
done
echo "timed out waiting for the build to start" >&2; exit 1
