# Conventions & API-style depth — `authoring-api-reference`

Depth for the per-section method (SKILL.md Step 5). Load when filling those sections. The endpoints/fields/errors always come from the handed-in api-spec contract; what follows are the *conventions* the reference is held to, grounded in established public-API-docs practice.

## Authentication flows (deepens cond-1)

Name the scheme/flow precisely — "uses OAuth" is not enough:

- **Static API key** — passed in a header (`Authorization: Bearer <key>` or `X-API-Key`). Simplest; document where to obtain + rotate it.
- **OAuth 2.0 flows** — pick the one the API uses:
  - **Authorization Code** — server-side web apps; the most secure interactive flow.
  - **Client Credentials** — machine-to-machine / service accounts (no user present).
  - **PKCE** — SPAs and native/mobile (Authorization Code + a proof key).
  - Avoid **Resource-Owner-Password** except for legacy migration.
- **Scopes & least-privilege** — document the available scopes; grant the minimum; request additional scopes incrementally (e.g. `profile:read` at signup, `profile:write` later).
- **Token lifecycle** — short-lived access token (e.g. ~1h) + a refresh token; document the refresh call and what to do on expiry.
- **Show success AND failure** — the worked request that authenticates, and the `401`/`403` response on a bad/missing/expired/under-scoped credential.
- Conceptual caution to state: holding a token is delegated **authorization** (what a client may do), not proof of **identity**.

## Error model — RFC 9457 Problem Details (deepens cond-3)

Document ONE consistent error shape, once:

- Prefer **RFC 9457 Problem Details for HTTP APIs** — `Content-Type: application/problem+json`, members `type`, `title`, `status`, `detail`, `instance`, plus domain extensions. (RFC 9457 obsoletes RFC 7807; same model.) Or document the API's own consistent shape.
- Carry a **machine-readable `code`** distinct from the HTTP status, so clients branch on a stable value rather than parsing prose.
- Use the **semantically-correct status**: `429` for rate-limit (not a generic `400`), `409` conflict, `422` validation (where used), `410 Gone` for a sunset resource (not `404`).
- A **status-code table** (code → cause → remedy) read once, plus **per-endpoint error rows** naming the failures each operation returns.
- A reference covering only `2xx` is incomplete — failure modes are part of the reference, not an appendix.

## Rate limits, retries & idempotency (deepens cond-4)

For an API that rate-limits or accepts writes:

- The **limit** (requests/window, per key/account), the **`429 Too Many Requests`** signal.
- **`Retry-After`** — the authoritative "when you may retry"; clients should prefer it over their own backoff.
- **`RateLimit-Limit` / `RateLimit-Remaining` / `RateLimit-Reset`** (and legacy `X-RateLimit-*`) where present — note they are typically **replaced by `Retry-After` on a `429`**, so document both.
- **Exponential backoff + jitter** (randomize the delay so retries don't synchronize).
- **Idempotency keys** for safe retried writes: a client sends a unique key; the server detects the duplicate and returns the **original** response instead of re-processing (so a network-retried `POST` doesn't double-create/charge). Document the header name, the de-dup window, and the behavior on key reuse. Proportional — a read-only / non-limiting API omits what doesn't apply.

## Pagination / filtering / sorting (cond-10)

For an API with list operations, document the model ONCE at the reference level so a caller learns one interface:

- **Model:** **cursor-based** for large/frequently-changing sets (stable under inserts, performant at scale); **offset/page-based** for small/stable sets (simpler; often capped, e.g. first 100 pages / 10k records → `400` beyond).
- **Standard parameter names** across all list endpoints: `limit` (page size) + `after`/`before` or `cursor` (cursor), or `page`/`per_page` (offset).
- **Response metadata:** `has_more`, `next_cursor` (and `total_count` where feasible), or a `Link` header.
- **Page size:** a default + a documented **maximum**.
- **Last-page signal:** an empty `next_cursor` / `has_more: false`.
- **Stable, tie-broken sort:** sort on an indexed field; for a non-unique sort field (e.g. a timestamp) append a unique secondary key (the record `id`) as a **tie-breaker** so ordering is deterministic across pages — required for both cursor and offset correctness.
- **Filtering/sorting conventions:** which fields are filterable/sortable and the syntax.
- Show a worked "fetch the next page" example. Proportional — a non-listing API has none.

## API-style overlays (authoring aids — proportional)

A reference's shape shifts by API style. Apply the relevant overlay; don't bloat a REST reference with sections for surfaces the API doesn't have. The reviewer judges the OUTCOME via the existing conditions, never the presence of a named section.

- **REST (default)** — resources + HTTP verbs, status codes, the per-endpoint path table, optional HATEOAS links.
- **GraphQL** — one endpoint + a typed schema. Document **types/fields** + **queries / mutations / subscriptions** + **introspection** + the partial-success error model (`errors[]` alongside `data`). The REST per-endpoint path table mis-fits — "every operation documented" maps to each query/mutation/subscription.
- **gRPC / RPC** — the `.proto` service definition, methods, **unary vs server/client/bidi streaming**, gRPC status codes, generated clients.
- **Webhooks / event-driven** — see the dedicated method below (the substantive overlay).
- **Streaming / WebSocket / SSE** — connection lifecycle (open/auth/close), the message/frame schema, reconnection + resume (`Last-Event-ID` for SSE), heartbeats/backpressure.

### Webhook / event documentation (the substantive overlay)

Webhooks are "operations in reverse" — the API calls the consumer. A reference for an event-driven API documents:

- **Event catalog** — every event type that fires (e.g. `invoice.paid`, `user.created`); the analog of the endpoint index. Missing the catalog fails cond-2 ("every operation documented").
- **Payload schema + a worked example per event** (typed, referencing the core objects).
- **Signature verification** — HMAC computed over the **raw request body** (the framework must not mutate it), with the **timestamp included in the signed payload** so the consumer can reject replays older than a few minutes. Security-critical; missing it fails cond-3.
- **Delivery semantics** — **at-least-once** delivery → a **delivery-ID idempotency key** (distinct from the event ID, since one event may be redelivered on retry) so the consumer de-dups; **retries with exponential backoff** (e.g. 5s → 25s → 125s → 625s) + a give-up/dead-letter policy; the **ack contract** (respond `2xx` within N seconds — e.g. 30s — or the delivery is treated as failed).
- **AsyncAPI** (or OpenAPI 3.1 `webhooks`) is the event-contract analog of OpenAPI; the events trace to it the way endpoints trace to the REST contract.

## The medium boundary (what this markdown artifact does NOT own)

The artifact is textual markdown today; the method is medium-independent. The **rendered docs site** (Redocly/Mintlify/Scalar/Stoplight) owns — and the reviewer does NOT judge in the markdown — full-text/AI **search**, the interactive **try-it / API explorer / Postman collection**, and the docs site's **accessibility/i18n**. Order endpoints the way a developer encounters them (create → retrieve → list → update → delete within a resource group) and keep one name per concept; that IA/consistency is the author's, judged as quality, not as a separate condition.
