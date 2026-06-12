# Validation: poll-queue-item.sh

- **Method**: syntax check (`bash -n`); poll logic verified against the queue-item contract (`references/patterns.md`, swaggy-jenkins `getQueueItem` schema).
- **Tools**: `bash -n` (clean); shellcheck not installed — skipped; `jq` 1.8.1 present.
- **Date**: 2026-06-12
- **Exit codes**: `bash -n`: 0.

## Captured output

`bash -n` clean. Polls `<queue-item-url>/api/json` up to 60×3s; exits 1 on `.cancelled`, prints `.executable.url` + `build_number` when `.executable.number` appears, and logs `.why` to stderr while waiting — the documented queue-item-to-build transition.

## Caveats

- Not executed live (needs a real server) — Phase 2.D smoke.
- The queue item is ephemeral (~5 min post-completion); the script is meant to be called promptly after `trigger-build.sh`.
