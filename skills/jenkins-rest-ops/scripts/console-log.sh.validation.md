# Validation: console-log.sh

- **Method**: syntax check (`bash -n`); path verified against `assets/endpoint-index.md`.
- **Tools**: `bash -n` (clean); shellcheck not installed — skipped.
- **Date**: 2026-06-12
- **Exit codes**: `bash -n`: 0.

## Captured output

`bash -n` clean. GETs `job/<name>/<build>/consoleText` (default `lastBuild`) — the full plaintext console log. The script comment points at `logText/progressiveText?start=<offset>` for incremental streaming.

## Caveats

- Not executed live (needs a real server + build) — Phase 2.D smoke.
