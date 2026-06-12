# Sources — cloudflare-pages-ops provenance

CLI-first on the official Wrangler CLI with a REST fallback grounded on Cloudflare's official OpenAPI (the Pages slice). All web content was sanitized before use; facts are paraphrased, never lifted verbatim.

## Authoritative (bundled)

- `assets/cloudflare-pages-openapi.json` — the **Pages-only slice** of Cloudflare's official OpenAPI (OpenAPI 3.0.3), extracted from `github.com/cloudflare/api-schemas` `openapi.json` (the full spec is ~10 MB / 1986 paths). The slice = the 11 account-scoped `/pages/...` paths + their transitive `$ref` closure (19 schemas; 0 dangling refs). Authoritative for paths, methods, params, body schemas, the `pages_stage` enums, and the response envelope.

## Official

- Cloudflare API docs — `https://developers.cloudflare.com/fundamentals/api/` — Bearer scoped-token auth, token creation, the `{success, errors, messages, result}` envelope, and the 1,200 req/5 min rate limit.
- Wrangler Pages commands — `https://developers.cloudflare.com/workers/wrangler/commands/` (pages) — the verified `pages project create` / `pages deploy` / `pages project list` / `pages deployment list|tail` commands + flags.
- Wrangler system environment variables — `https://developers.cloudflare.com/workers/wrangler/system-environment-variables/` — `CLOUDFLARE_API_TOKEN` / `CLOUDFLARE_ACCOUNT_ID` for headless auth.
- Cloudflare Pages — Direct Upload — `https://developers.cloudflare.com/pages/get-started/direct-upload/` — the deploy model + Direct-Upload-vs-Git distinction.

## Verified live

- None yet. The Phase 2.D live smoke (create a project → deploy a tiny build → read deployment status, add a custom domain) is pending the owner's `CLOUDFLARE_API_TOKEN` + `account_id`.

## Flagged uncertain (carry as "confirm live")

- The exact dashboard label for the Pages token permission ("Account → Cloudflare Pages → Edit") was not quoted verbatim — the account scope + Edit level are certain (account-scoped REST paths + Edit = CRUDL), only the literal UI string is unconfirmed.
- `wrangler pages deployment tail`'s exact filter flag names were not individually quoted (the subcommand + its filtering capability are confirmed).
