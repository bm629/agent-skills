# Validation: add-custom-domain.sh

- **Method**: syntax check (`bash -n`); path/method/body verified against `python3 scripts/endpoint.py pages-domains-add-domain`.
- **Tools**: `bash -n` (clean); shellcheck not installed — skipped; `jq` 1.8.1 present.
- **Date**: 2026-06-12
- **Exit codes**: `bash -n`: 0.

## Captured output

`bash -n` clean. POSTs `/accounts/<id>/pages/projects/<project>/domains` with `{"name":"<domain>"}` and a Bearer token — matching the resolved `pages-domains-add-domain` schema (`name` required). REST is the only path (Wrangler has no custom-domain command).

## Caveats

- Not run live (needs the token + account_id + a project) — Phase 2.D smoke.
- The domain must be on a Cloudflare zone with DNS pointed at the project. Check the `{success, errors, messages, result}` envelope, not just the HTTP status.
