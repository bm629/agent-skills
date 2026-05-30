# Atlassian REST — per-API patterns

Confluence Cloud v2 and Jira Cloud v3 differ; apply the right column.

## Auth (both)

HTTP Basic with a Cloud email + API token:
```
curl -u "$email:$<token_env>" \    # token_env e.g. ATLASSIAN_WORK_API_TOKEN
     -H "Accept: application/json" -H "Content-Type: application/json" ...
```
`$email` and `token_env` come from the account record; the token value is read from the environment only (see `credentials.md`).

## Base URL

- **Confluence v2:** `<base_url>/wiki/api/v2/<path>` — spec paths are relative (e.g. `/pages`). `base_url = https://<site>.atlassian.net`.
- **Jira v3:** `<base_url>/<path>` — spec paths already include `/rest/api/3/…`. Don't add `/wiki`.

## Pagination

- **Confluence (cursor):** query `limit` + `cursor`; response `{ results: [...], _links: { next? } }`. Page by following `_links.next` (a relative URL with the next cursor) until it's absent.
- **Jira (offset — most endpoints):** query `startAt` + `maxResults`; response `{ startAt, maxResults, total, isLast, values|issues: [...] }`. Page by incrementing `startAt` until `isLast` or `startAt + maxResults >= total`.
- **Jira (token — newer, incl. `/search/jql`):** query `maxResults` + `nextPageToken`; response carries `nextPageToken` + `isLast`. Page by passing the returned token until absent.

## Errors

- **Jira:** `ErrorCollection` = `{ "errorMessages": [...], "errors": { "<field>": "<msg>" }, "status": <int> }`. Check both `errorMessages` and `errors`.
- **Confluence:** inline JSON, typically `{ "errors": [ { "status", "code", "title", "detail" } ] }` (no single named schema).
- Statuses: 400 (read the error body), 401 (auth), 403 (perms), 404 (not found / no access), 409 (Jira conflict).

## Rate limits

- **Jira:** HTTP **429** with a `Retry-After` (seconds) header — sleep that long; exponential backoff on repeats.
- **Confluence:** 413 (payload too large → shrink body); 503 transient → backoff + retry.

## Deletes & query constraints (verified live)

- **Confluence delete is two-stage** (pages, blogposts, other content): `DELETE /wiki/api/v2/pages/{id}` (or `/blogposts/{id}`) → 204 but only **trashes** (GET still 200, `status: trashed`). `DELETE …/{id}?purge=true` → 204 permanently removes — **only after it's trashed** (purge-without-trash is a no-op). GET then 404.
- **Jira `/search/jql` needs a bounded query:** ordering-only or empty JQL → `400 ErrorCollection` "Unbounded JQL queries are not allowed here." Include a restriction (`project = …`, `created >= -30d`, …).

## Useful query knobs

- **Jira:** `expand=` (which sections to expand), `fields=` (limit returned fields).
- **Confluence:** `body-format` ∈ {`storage`, `atlas_doc_format`} on GET (controls the returned body representation).
