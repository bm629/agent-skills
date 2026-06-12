# The `netlify` CLI — the common path

The `netlify` CLI (npm `netlify-cli`, Node ≥18) is the ergonomic common path. It reads the token from `NETLIFY_AUTH_TOKEN` (or `--auth <token>`), so it runs headlessly. Pass `--json` for machine-readable output and `--force` to skip confirmation prompts. See `assets/cli-index.md` for the quick command list.

## Non-interactive rules

- Set `NETLIFY_AUTH_TOKEN` (from the injected var) and add `--json`. **Never** `netlify login` / `netlify logout` — those are the interactive OAuth path the contract forbids.
- `netlify status --json` confirms auth + the linked site.
- The CLI keys deploys on the opaque **`site_id`** (stored in `.netlify/state.json` after a link). A fresh CI checkout has no link state — always pass `--site <id>` explicitly.

## Core commands

| Need | Command |
|---|---|
| Create a site | `netlify sites:create --name <name> [--account-slug <slug>] --disable-linking --json` |
| List sites | `netlify sites:list --json` |
| Deploy (draft/preview) | `netlify deploy --dir <dir> --site <site_id> --json` |
| Deploy (production) | `netlify deploy --dir <dir> --site <site_id> --prod --json` |
| Skip the build step | add `--no-build` (there is **no** `--build` flag — the CLI builds by default) |
| Named preview | add `--alias <name>` |
| Auth + link status | `netlify status --json` |
| Any REST op | `netlify api <operationId> --data '<json>'` (escape hatch) |
| Enumerate REST ops | `netlify api --list` |

## The escape hatch — full REST coverage from the CLI

`netlify api <operationId> --data '<json>'` calls any Netlify REST operation by operationId. For a **path-params-only** op the payload keys map directly (e.g. `netlify api getSiteDeploy --data '{"site_id":"<id>","deploy_id":"<id>"}'`). For an op with a **request body**, the body-key convention is not pinned in the official docs — prefer the **pure REST `curl`** (`references/rest-api.md`) for body-carrying writes like `updateSite` / `createSiteDeploy`, where the body shape is unambiguous from the spec. Resolve any op's params/body with `python3 scripts/endpoint.py <operationId>`.

## Gotchas

- `--prod` vs draft: omit `--prod` → a draft/preview deploy (unique URL, production untouched); `--prod` → publish to the live site.
- `site_id` vs name/slug: `--name`/`--account-slug` are human-facing; every API op keys on the opaque `site_id`.
- Rate limits: 500 req/min general; **deploys 3/min, 100/day** — honor the `X-RateLimit-*` response headers.
- `--allow-anonymous` (deploy to a claimable site without auth) is **not** this skill's path — always deploy to a known `site_id` with the injected token.
