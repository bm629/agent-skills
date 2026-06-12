# Sources — netlify-ops provenance

CLI-first on the official `netlify` CLI with a REST fallback grounded on Netlify's official OpenAPI. All web content was sanitized before use; facts are paraphrased, never lifted verbatim.

## Authoritative (bundled)

- `assets/netlify-openapi.json` — Netlify's official OpenAPI, **Swagger 2.0** (Netlify API 2.55.0; host `api.netlify.com`, basePath `/api/v1`; 113 paths / 174 ops), fetched from `https://open-api.netlify.com/swagger.json` (also npm `@netlify/open-api`). Authoritative for operationIds, paths, methods, params, and body/response schemas.

## Official

- Netlify API docs — `https://docs.netlify.com/api/get-started/` — the base URL, Bearer PAT auth, the PAT-creation UI + expiry, and the rate limits (500 req/min general; deploys 3/min, 100/day) + `X-RateLimit-*` headers.
- Netlify CLI docs — `https://cli.netlify.com/commands/` — the verified `deploy` / `sites` / `api` commands and flags (`--dir`/`--prod`/`--json`/`--no-build`/`--site`/`--auth`, `sites:create --name`/`--account-slug`, `netlify api <op> --data`).
- `netlify/context-and-tools@netlify-cli-and-deploy` (~496 installs, OFFICIAL maintainer) — source material (sanitized clean): link/init mechanics, `.netlify/state.json` site-id, env management. Auth rewritten: it leads with interactive `netlify login`; this skill uses the injected token only.

## Community / unofficial (flagged)

- `openai/skills@netlify-deploy` (~1.7K installs, community) — source material (sanitized clean): the deploy recipe, framework build-dir defaults, the `netlify api` escape-hatch example, scenario patterns. Auth rewritten: it is login-first (`netlify login` primary, `NETLIFY_AUTH_TOKEN` secondary); this skill drops `login`/`logout` and treats the injected token as the sole auth.

## Verified live

- None yet. The Phase 2.D live smoke (create a site → deploy a tiny build → read status, set+verify a custom domain) is pending the owner's Netlify PAT.

## Flagged uncertain (carry as "confirm live")

- `deploy.state` value set (building/uploading/processing/ready/error) — from docs, not a spec enum.
- The `netlify api <op> --data` body-key convention for body-carrying ops (OpenAPI body-param name vs a js-client `body` key) is not pinned by the docs — body-carrying writes (`updateSite`, `createSiteDeploy`) use the unambiguous pure-REST `curl`; path-params-only ops use the escape hatch.
- `CI=true` as a CLI prompt-suppressor — unverified; rely on `--json` / `--force` + the token env var.
