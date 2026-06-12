# Validation: set-custom-domain.sh

- **Method**: syntax check (`bash -n`); path/method/body verified against `python3 scripts/endpoint.py updateSite`.
- **Tools**: `bash -n` (clean); shellcheck not installed — skipped; `jq` 1.8.1 present.
- **Date**: 2026-06-12
- **Exit codes**: `bash -n`: 0.

## Captured output

`bash -n` clean. PATCHes `/api/v1/sites/<site_id>` with `{"custom_domain":"<domain>"}` and a Bearer token — matching the resolved `updateSite` schema (`site_id` path param + the `site` body with a `custom_domain` field). Uses the **pure REST** curl (not the `netlify api` escape hatch) because the escape-hatch body-key convention for body-carrying ops is unverified; the REST body is unambiguous from the spec.

## Caveats

- Not run live (needs `NETLIFY_AUTH_TOKEN` + a site) — Phase 2.D smoke.
- Setting the domain does not make it resolve — follow with DNS config (`configureDNSForSite` / `dns_zones` records).
