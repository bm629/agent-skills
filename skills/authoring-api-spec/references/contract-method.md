# The contract spine — method depth (`authoring-api-spec`)

Worked depth for the contract-completeness spine the Step-7 self-check asserts. Load when filling a section needs more than the body's one-liner. Portable provenance in `sources.md`.

## Operations, resources & method semantics

- **One style, its notation.** A project uses one style; render in it (OpenAPI for REST, SDL for GraphQL, proto for gRPC). The rigor (typed both sides, complete errors, auth, examples, versioning) is identical; only the notation adapts.
- **REST resources are nouns** (plural collections + item subpaths): `GET /invoices`, `POST /invoices`, `GET /invoices/{id}`, `PATCH /invoices/{id}`. Avoid verbs in paths (`POST /createInvoice` is RPC-over-REST) except genuine actions (`POST /invoices/{id}:void`).
- **HTTP method semantics (RFC 9110):** `GET` safe+idempotent (never mutates); `PUT`/`DELETE` idempotent; `PATCH` partial (idempotent only if the patch is); `POST` neither. The method matches the operation's semantics.
- **Status-code selection is part of the contract.** Success: `200` (read/update+body), `201`+`Location` (create), `202` (async accepted), `204` (no-body success). Client error: `400`/`422` (validation), `401` (unauthenticated), `403` (forbidden/insufficient-scope — distinct from `401`), `404` (not found), `409` (conflict/duplicate), `429` (rate-limited). Server: `500` (fault), `503` (unavailable). Choose deliberately, not `200` for everything.
- **Idempotency for unsafe operations.** Where a retried `POST` could duplicate (a payment), state an `Idempotency-Key` header the server dedupes on.
- **Coverage runs off the feature-spec.** Every behavior → ≥1 operation; every operation → a behavior (a "Maps to" line). No orphan/invented endpoint, none missing.
- **GraphQL:** `Query` (reads, parallel) / `Mutation` (writes, serial) / `Subscription` (stream). **gRPC:** `service` + `rpc` methods (unary / server-streaming / client-streaming / bidi).

## Request & response schema rigor (typed both sides)

- Each field carries **type + required/optional + constraints** (length/range/enum/format/pattern). A money field is `integer, minor units, >0`, not "a number".
- **GraphQL nullability is the type** (`String!` non-null vs `String`). **proto3** fields default optional on the wire — state required-ness in prose.
- **Every response keyed to a status + a typed body.** The failure responses are part of the schema set (handed to the error model). A happy-path-only operation is not done.
- **Shared DTOs defined once + referenced** (`$ref` / SDL type / proto message); never re-inline the same shape (it drifts). OpenAPI 3.1/3.2 is JSON-Schema-2020-12-aligned; compose via `allOf`/`oneOf` + `discriminator`.
- **Wire DTO references the data-model, not redefines it.** Where a DTO projects a stored entity, reference the data-model + note only the deltas (computed/omitted/flattened/renamed). A DTO is not a stored row. Greenfield (no data-model): the DTO stands alone.

## The complete error model (the signature)

Two halves, both required:

1. **One consistent error shape for the whole API.** REST → **RFC 9457 Problem Details** (`application/problem+json`; `type`/`title`/`status`/`detail`/`instance` + extension members for the machine `code` + `requestId`). GraphQL → the top-level `errors` array (`extensions.code`). gRPC → `google.rpc.Status` + the canonical codes. Inventing a different error body per endpoint is the cardinal error.
2. **Every named failure case enumerated per operation,** each with status + **machine code** (the client branches on it — the status is too coarse) + a **request/trace id** + **retryability** (`429`/`5xx` retryable after `Retry-After` with backoff+jitter; `4xx` not). Not every operation has every case (a `GET` has no `409`), but every case it *can* produce is named. A spec listing only `2xx` fails.

## Auth & authorization

- Name the **scheme + where the credential goes** — API key (header), OAuth 2.0 (token), JWT bearer, mTLS. OpenAPI declares these in `securitySchemes` + applies via `security`.
- **OAuth flow per client type:** auth-code + **PKCE** for user-facing/public clients (the default even for confidential clients now); client-credentials for service-to-service; device-authorization for input-constrained devices. (Implicit + password grants are deprecated — don't specify for a new API.)
- **Authorization is per-operation:** every non-public operation names its scope/role, mapped to the operation list. "Authenticated" without a per-operation scope is under-specified.
- **Token lifecycle** (expiry/refresh/revocation) + **transport** (HTTPS; no credential in a URL).

## Pagination, filtering, sorting & rate-limits (collections)

- **Cursor-based** (opaque, stable under inserts) for large/dynamic sets; **offset** for small/static. Define the request params + the response envelope (`next_cursor`/`has_more` or a `Link` header) + **default + max page size**. GraphQL → Relay Cursor Connections (`edges { cursor node }` + `pageInfo`).
- **Sorting needs a stable tie-breaker** — a secondary sort on a unique key (id) so rows with equal primary-sort values keep a deterministic order across pages (without it, cursor pagination shuffles → a skip/duplicate).
- **Rate limits:** the limit per credential, the headers (`RateLimit-*`/`Retry-After`, or the newer structured `RateLimit`+`RateLimit-Policy`), the `429`+`Retry-After` behavior.

## Worked examples

≥1 full request/response pair per primary operation + a representative error example, **consistent with the schemas** (same field names, types, status codes, error shape). An example that contradicts its schema is a defect (a field the schema lacks, a wrong type, a `200` where the schema says `201`).
