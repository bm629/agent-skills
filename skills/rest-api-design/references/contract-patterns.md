# Contract patterns — success envelope, pagination, versioning, auth, rate limiting

Load when shaping responses/pagination or deciding versioning/auth/rate-limit stance.

## Success envelope

Apply **one** envelope across the whole API.

- **Single resource** — return the representation directly, or a thin `{"data": {...}}` wrapper. Either is fine; pick one and be consistent.
- **Collection** — always `data` (the array) + a `pagination`/`meta` block + optional `links`:

```json
{
  "data": [ { "id": "ord_1", "total": 4200 }, { "id": "ord_2", "total": 1799 } ],
  "pagination": { "next_cursor": "b3JkXzI", "has_more": true },
  "links": { "self": "/v1/orders?limit=2", "next": "/v1/orders?cursor=b3JkXzI&limit=2" }
}
```

Use ISO 8601 / RFC 3339 timestamps (`2026-06-08T10:30:00Z`). Keep field naming consistent (`snake_case` or `camelCase` — pick one for the whole API).

## Pagination — cursor (default) vs offset

Every collection endpoint is paginated. Default `limit` 20, hard-max 100; reject a larger `limit` with 422.

| | Cursor / keyset (default) | Offset / page |
|---|---|---|
| Deep-page performance | Constant (indexed seek) | Degrades — DB scans + discards skipped rows (large offsets can be ~10x+ slower) |
| Consistency under writes | Stable — no skips/dupes | Drifts — concurrent inserts/deletes skip or repeat rows across pages |
| Random page access (jump to page 50) | No | Yes |
| Total count | Usually omitted (count is expensive) | Available |
| Best for | Large/changing data, feeds, infinite scroll | Small, stable datasets; admin tables needing page numbers + totals |

**Cursor response:**
```json
{ "data": [ ... ], "pagination": { "next_cursor": "eyJpZCI6MzB9", "has_more": true } }
```
A cursor is an **opaque** token (base64 of the last item's sort key) — clients pass it back, never construct it.

**Offset response:**
```json
{ "data": [ ... ], "pagination": { "offset": 20, "limit": 10, "total": 145, "has_more": true } }
```

Default to cursor; choose offset only when random access or a live total count is a real requirement and the dataset is small/stable. Apply filters/sort **before** paginating. Support sorting via an explicit param (`?sort=-created_at`); for cursor pagination the sort key must be embedded in the cursor.

## Versioning

- **URL path is the default:** `/v1/orders`. Visible, debuggable, CDN-cacheable, lets versions run in parallel. Alternative: media-type/header versioning (`Accept: application/vnd.example.v2+json`) when clean stable URLs outweigh discoverability.
- **Major-version-only.** Use `v1`, `v2` — not `v1.1`. A new version is a promise about a set of breaking changes.
- **Breaking** (bump major): remove/rename a field, change a field's type, add a required request field, change the status code for the same scenario, change auth. **Non-breaking** (no bump): add an endpoint, add an optional field, add an optional param. Design clients as **tolerant readers** — ignore unknown response fields so additive changes don't break them.
- **Deprecation lifecycle** (RFC 8594 headers):
  ```http
  Deprecation: true
  Sunset: Wed, 31 Dec 2026 23:59:59 GMT
  Link: </v2/orders>; rel="successor-version"
  ```
  Announce well ahead (commonly 6–12 months), run old + new in parallel, then return `410 Gone` after the sunset date. Keep at most ~2–3 active versions.

## Auth in the contract

- **Bearer / JWT** for user-facing APIs: `Authorization: Bearer <token>`.
- **API key** for service-to-service: a header such as `X-API-Key: <key>` (header, not query string — query strings leak into logs).
- **Always HTTPS.** Never accept credentials over plain HTTP.
- Declare auth in OpenAPI as `components.securitySchemes` + a `security` requirement, applied globally or per operation. Document which scopes/permissions an operation needs; a missing/invalid credential is `401`, an insufficient one is `403`.

## Rate limiting

- **Baseline (always works):** on limit, return `429 Too Many Requests` with a **`Retry-After`** header (seconds, or an HTTP date) — defined by RFC 9110, understood everywhere.
- **Advertise quota:** the de-facto `X-RateLimit-Limit` / `X-RateLimit-Remaining` / `X-RateLimit-Reset` headers are widely deployed and a safe choice today.
- **Emerging standard:** the IETF "RateLimit header fields" work (a structured `RateLimit` field + `RateLimit-Policy`) is not yet a published RFC and has shifted shape — treat it as forward-looking, not the thing to depend on. If both `Retry-After` and a reset hint are present, `Retry-After` wins.

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 30
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1779000000
Content-Type: application/problem+json
```
The 429 body is still a problem+json object (see `error-model.md`).
