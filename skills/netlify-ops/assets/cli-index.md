# Netlify CLI index — the common path

The ergonomic common path is the `netlify` CLI (npm `netlify-cli`, Node ≥18). It reads the token from `NETLIFY_AUTH_TOKEN` (or `--auth <token>`), so it runs headlessly — **never** `netlify login`/`logout` in an agent flow. Pass `--json` for machine-readable output and `--force` to skip confirmation prompts. The REST long tail is reachable from the CLI via the escape hatch.

## Auth (headless)

- `NETLIFY_AUTH_TOKEN=<token> netlify <cmd>` — or `netlify <cmd> --auth <token>`. The token is the injected PAT (by variable name, never printed). No interactive login.
- `netlify status --json` — confirm auth + the linked site.

## Sites

- `netlify sites:create --name <name> [--account-slug <slug>] [--disable-linking]` — create a site. Returns the site as JSON; its id is the `id` field (`--json` returns the id under `id`, not `site_id`) — pass that id as `--site` to deploy.
- `netlify sites:list --json` — list your sites.
- Get/update a site by id → use the escape hatch (`netlify api getSite --data '{"site_id":"<id>"}'`).

## Deploy

- `netlify deploy --dir <dir> --site <site_id> [--message <m>] [--json]` — a **draft/preview** deploy (unique URL; does not touch production).
- `netlify deploy --dir <dir> --site <site_id> --prod [--json]` — a **production** deploy (publishes to the live URL).
- `--no-build` to skip the build step (the CLI builds by default; there is **no** `--build` flag). `--alias <name>` for a named preview. In a fresh CI checkout there is no `.netlify/state.json`, so always pass `--site <id>` explicitly.

## Status

- `netlify status [--json]` — auth + linked-site status.
- A specific deploy's state → `netlify api getSiteDeploy --data '{"site_id":"<id>","deploy_id":"<id>"}'` (the `state` field).

## Custom domain

- No first-class `netlify domains:*` for setting a site's custom domain — use the **pure-REST** `updateSite` PATCH (the escape-hatch body-key for body-carrying ops is unverified — see "The escape hatch" below): `bash scripts/set-custom-domain.sh <site-id> example.com`, i.e. `curl -X PATCH .../api/v1/sites/<id> -H "Authorization: Bearer $NETLIFY_AUTH_TOKEN" -d '{"custom_domain":"example.com"}'`. Then manage DNS via the DNS ops (`configureDNSForSite`, `dns_zones` / `dns_records`).

## The escape hatch (full REST coverage)

- `netlify api <operationId> --data '<json>'` — call ANY Netlify REST operation by operationId.
- `netlify api --list` — enumerate every method. Resolve a method's params/body with `python3 scripts/endpoint.py <operationId>` or scan `assets/endpoint-index.md`.
