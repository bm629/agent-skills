# Validation: deployment-status.sh

- **Method**: syntax check (`bash -n`); path verified against `python3 scripts/endpoint.py pages-deployment-get-deployment-info`.
- **Tools**: `bash -n` (clean); shellcheck not installed — skipped.
- **Date**: 2026-06-12
- **Exit codes**: `bash -n`: 0.

## Captured output

`bash -n` clean. GETs `/accounts/<id>/pages/projects/<project>/deployments/<deployment_id>` with a Bearer token — returns the deployment incl. `latest_stage.{name,status}`. Poll until the `deploy` stage reaches `status: success` (or `failure`).

## Caveats

- Not run live (needs the token + account_id + a deployment) — Phase 2.D smoke.
- `latest_stage.name` ∈ queued/initialize/clone_repo/build/deploy; `status` ∈ success/idle/active/failure/canceled. Check the `{success, errors, messages, result}` envelope.
