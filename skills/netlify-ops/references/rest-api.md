# The Netlify REST API — the long-tail fallback

The REST API is the comprehensive long tail under `https://api.netlify.com/api/v1`, auth `Authorization: Bearer <token>`. Use it when the CLI has no first-class command (custom domain, fine-grained reads, DNS). Scan `assets/endpoint-index.md` for an operation, resolve its shape with `python3 scripts/endpoint.py <operationId>`, then `curl`.

## Pattern

- **Base + auth:** `curl -H "Authorization: Bearer $NETLIFY_AUTH_TOKEN" "https://api.netlify.com/api/v1/<path>"`.
- **ids:** opaque `site_id` / `deploy_id` strings.
- **Resolve, don't guess:** the bundled spec is Swagger 2.0; `endpoint.py` `$ref`-resolves `#/definitions`, body params, `allOf`, and path-level params. Never load the ~690 KB spec into context.

## Priority operations

| Need | operationId | Method + path | Body / key fields |
|---|---|---|---|
| Create a site | `createSite` | POST `/sites` | body `site` (`{name, custom_domain, …}`); query `configure_dns` |
| Create site in a team | `createSiteInTeam` | POST `/{account_slug}/sites` | path `account_slug`; body `site` |
| Deploy to a site | `createSiteDeploy` | POST `/sites/{site_id}/deploys` | body `deploy` (inline: digest `files` map or `zip`) |
| Set custom domain | `updateSite` | **PATCH** `/sites/{site_id}` | body `{custom_domain, domain_aliases}` |
| Deploy status | `getSiteDeploy` | GET `/sites/{site_id}/deploys/{deploy_id}` | → `state` |
| Deploy by id | `getDeploy` | GET `/deploys/{deploy_id}` | → `state` |
| List sites | `listSites` | GET `/sites` | — |
| Get a site | `getSite` | GET `/sites/{site_id}` | — |
| List a site's deploys | `listSiteDeploys` | GET `/sites/{site_id}/deploys` | — |
| Delete a site | `deleteSite` | DELETE `/sites/{site_id}` | — |
| Site DNS | `getDNSForSite` / `configureDNSForSite` | GET/PUT `/sites/{site_id}/dns` | — |
| DNS zones / records | `*DnsZone*` / `*DnsRecord*` | `/dns_zones…` | — |

## The digest-deploy protocol (REST `createSiteDeploy`)

The CLI `netlify deploy --dir` wraps this; do it by hand only when the CLI is unavailable:

1. POST `createSiteDeploy` with `files` = a map of `{path: SHA1-of-contents}` (the full manifest).
2. The response carries a **`required`** array — the SHA1s the server does **not** yet have.
3. **Upload exactly those** files (one PUT per required digest). The deploy only reaches `state: ready` once all required files are uploaded.

(There is a parallel `required_functions` for serverless bundles, and a simpler `zip` body — raw `application/zip` — as an alternative to the digest manifest.)

## State + limits

- `deploy.state`: `new`/`building` → `uploading`/`uploaded` → `processing` → `ready`, or `error`. (Lifecycle values from Netlify docs — the spec declares `state` as a free string, not an enum; confirm against a live deploy.)
- Rate limits: 500 req/min general; **deploys 3/min, 100/day**. Honor `X-RateLimit-Limit` / `-Remaining` / `-Reset`.
