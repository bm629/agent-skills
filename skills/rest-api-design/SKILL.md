---
name: rest-api-design
description: >
  Use when designing a REST/HTTP API surface and its contract — choosing
  resources and URLs, picking HTTP methods and status codes, defining the
  error model (RFC 9457 problem+json), shaping the success/pagination
  envelope, versioning, auth, and rate limiting, then expressing the design
  as an OpenAPI 3.1 contract. This is the design discipline that sits ABOVE
  a web framework: it produces the decisions and the contract, not the
  handler code. Keywords: REST API design, HTTP API, resource modeling,
  status codes, problem details, RFC 9457, pagination, API versioning,
  rate limiting, OpenAPI 3.1 contract.
version: "1.0.0"
forge:
  status: reviewed
  forged: 2026-06-08
  reviewed: 2026-06-08
---

# `rest-api-design` — SKILL.md

> **Variant:** standard · **When to use:** the skill is invoked, applies the design decisions below to a resource surface, and returns a coherent contract; control passes back to the caller.

## Overview

This skill is the **design discipline for a REST/HTTP API and its contract** — the layer above any web framework. It carries the opinionated defaults a senior engineer applies when turning a set of domain nouns into a consistent, evolvable HTTP surface: how to name resources, which method and status code each operation gets, one machine-readable error shape (RFC 9457 problem+json), a structured success and pagination envelope, a versioning stance, where auth and rate limiting live, and how the whole thing renders as an OpenAPI 3.1 contract. Code shown is Python/FastAPI + Pydantic v2 flavored, but every decision is language-agnostic. Framework mechanics (routers, dependency injection, `response_model`) and schema modeling belong to the `fastapi` and `pydantic-v2` skills — this skill references them and does not duplicate them.

## When to activate

- ✅ Designing a new API surface from a set of domain entities — what the endpoints, methods, and contract should be.
- ✅ Choosing the correct status code for an outcome, or deciding 400 vs 422, 401 vs 403, PUT vs PATCH.
- ✅ Defining or fixing the error model, the success envelope, or the pagination scheme of an API.
- ✅ Deciding a versioning, auth, or rate-limiting stance for an API.
- ✅ Turning an agreed REST design into an OpenAPI 3.1 contract.

**Do NOT activate when:**

- Writing the FastAPI handler/router/DI code for an already-designed endpoint → use the `fastapi` skill.
- Modeling the request/response data classes in depth → use the `pydantic-v2` skill.
- Authoring or generating a large OpenAPI document, linting it, or running SDK codegen → that is a dedicated OpenAPI-authoring/codegen concern (see `references/openapi-mapping.md` for the design→contract mapping and where to hand off).
- Designing a GraphQL or gRPC surface → out of scope; this skill is REST/HTTP only.

## Workflow

Apply these steps in order. Each step states an opinionated default; deviate only with a reason.

### Step 1: Model resources (nouns, not verbs)

- Resources are **nouns**; the HTTP method is the verb. `POST /orders`, never `POST /createOrder`.
- Collections are **plural and consistent**: `/users`, `/users/{id}`, `/users/{id}/orders`. Never mix `/user` and `/users`.
- **Cap nesting at 2 levels.** `/users/{id}/orders` is fine; `/users/{id}/orders/{oid}/items/{iid}` is not — promote the deep child to a top-level resource (`/order-items/{iid}`) and link to it.
- Identify resources from the domain nouns and their relationships before choosing any URL. Sub-resources express containment/ownership; cross-cutting things become their own top-level resource.
- Use lowercase, hyphenated path segments (`/order-items`), not `camelCase` or `snake_case`, in URLs.
- Do not leak internal/primary-key IDs that expose row counts or enumeration — prefer UUIDs or opaque IDs in the public contract.

### Step 2: Assign methods + honor idempotency

Per RFC 9110 HTTP semantics:

| Method | Use for | Safe | Idempotent |
|---|---|---|---|
| GET | read a resource/collection | yes | yes |
| POST | create in a collection; non-idempotent actions | no | **no** |
| PUT | **full replace** of a resource at a known URL | no | yes |
| PATCH | **partial update** (only the sent fields) | no | **no** |
| DELETE | remove a resource | no | yes |

- **PUT replaces, PATCH merges.** A PUT body is the complete new representation; omitted fields are cleared. A PATCH body carries only the fields to change. Don't use PUT for partial updates.
- POST and PATCH are **not idempotent**: a retried POST creates a duplicate. For create/charge operations that clients may retry, accept an **`Idempotency-Key` request header** (the Stripe convention, now an IETF draft) — store the key + first response and replay it on a repeat, so a network retry is safe.
- GET must have **no side effects**. If an operation mutates state, it is not a GET.

### Step 3: Pick the status code that matches the outcome

| Code | Meaning / when |
|---|---|
| 200 OK | successful GET/PATCH/PUT, or DELETE that returns a body |
| 201 Created | successful create — set a `Location` header to the new resource URL |
| 204 No Content | success with no body (typical DELETE, or PUT/PATCH returning nothing) |
| 400 Bad Request | **malformed** request — unparseable JSON, wrong shape, bad query encoding |
| 401 Unauthorized | **not authenticated** — missing/invalid credentials |
| 403 Forbidden | authenticated but **not allowed** to do this |
| 404 Not Found | resource does not exist (or is hidden from this caller) |
| 409 Conflict | request conflicts with current **state** — duplicate unique field, version clash |
| 422 Unprocessable Content | syntactically valid but **semantically invalid** — failed business/field validation |
| 429 Too Many Requests | rate limit exceeded — include `Retry-After` |
| 5xx | server fault — 500 generic, 503 unavailable; never blame the client |

- **400 vs 422:** 400 = the server could not parse/understand the request at all; 422 = it parsed fine but the values fail validation. Default new APIs to **422 for validation failures, 400 for parse failures**.
- **401 vs 403:** 401 = who are you (re-authenticate); 403 = I know who you are and you still can't.
- **Never return 200 with an error in the body.** The status code is the primary, machine-readable signal — a 200-wrapped failure breaks every client, proxy, and monitor.

### Step 4: Define ONE error model — RFC 9457 problem+json (default)

Every error response uses **`application/problem+json`** (RFC 9457, which obsoletes RFC 7807) with these members:

- `type` — a URI identifying the problem **type** (stable, documented; defaults to `"about:blank"` when there's nothing beyond the status code).
- `title` — short human summary of the type (for `about:blank`, the HTTP status phrase, e.g. `"Not Found"`).
- `status` — the HTTP status code, duplicated in the body.
- `detail` — human-readable explanation of **this** occurrence.
- `instance` — URI for this specific occurrence (e.g. the request path or a trace id).
- **extension members** — any extra domain fields; clients MUST ignore ones they don't recognize. Field-level validation errors go in an **`errors`** array (the RFC's recognized extension).

```json
{
  "type": "https://api.example.com/problems/validation-error",
  "title": "Your request parameters did not validate.",
  "status": 422,
  "detail": "The request body has 2 invalid fields.",
  "instance": "/orders",
  "errors": [
    { "detail": "must be a positive integer", "pointer": "#/quantity" },
    { "detail": "must be a valid email", "pointer": "#/customer/email" }
  ]
}
```

- Pick **one** model for the whole API and never mix. RFC 9457 is the default because it is a standard, machine-parseable, and self-describing.
- **Alternative (only if a house style mandates it):** the envelope `{"error": {"code": "...", "message": "...", "details": [...]}}`. It works but is non-standard; prefer problem+json for new APIs. Do not run both.
- FastAPI flavor: register an exception handler that returns `application/problem+json`; map `RequestValidationError` to a 422 problem with the `errors` array. See `references/error-model.md`.

### Step 5: Shape success + pagination as one envelope

- Single resource: return the representation. A thin, consistent wrapper (`{"data": {...}}`) is fine if applied **everywhere** — consistency beats cleverness.
- Collections are **always paginated** — never return an unbounded list. Default `limit` 20, hard-max 100, reject larger with 422.
- Use **one** envelope shape across all list endpoints: `data` (the items) + `pagination`/`meta` (the cursors/counts) + optional `links` (navigation URLs).
- **Cursor (keyset) is the default** for large/changing/feed-like data: stable under inserts, constant-time deep pages, no expensive total count. Use **offset/page** only for small, stable datasets that need random page jumps or a total count — it drifts (skips/dupes) under concurrent writes and slows badly on deep pages.
- See `references/contract-patterns.md` for both envelope shapes and the cursor-vs-offset decision.

### Step 6: Decide versioning, auth, and rate limiting

- **Versioning — URL path is the default:** `/v1/users`. Visible, debuggable, cache-friendly, lets versions run side by side. Header/media-type versioning is the alternative when clean URLs matter more than discoverability.
- Bump the **major** version only for **breaking** changes (removing/renaming a field, changing a type, adding a required field, changing a status for the same scenario). **Additive** changes (new endpoints, new optional fields) never bump it — design clients as **tolerant readers** that ignore unknown fields.
- Signal retirement with the `Deprecation` and `Sunset` headers (RFC 8594); return `410 Gone` after sunset.
- **Auth lives in the contract, not as an afterthought:** `Authorization: Bearer <token>` (JWT/OAuth) is the default for user-facing APIs; an API-key header (e.g. `X-API-Key`) for service-to-service. **Always HTTPS.** In OpenAPI these are `securitySchemes` + a `security` requirement (per-operation or global).
- **Rate limiting:** return **`429` + `Retry-After`** (the stable, RFC-9110 default). Advertise quota with the widely-deployed `X-RateLimit-Limit`/`-Remaining`/`-Reset` convention; the IETF `RateLimit`/`RateLimit-Policy` fields are the emerging standard but not yet an RFC — `429` + `Retry-After` is the safe baseline every client understands.

### Step 7: Express the design as an OpenAPI 3.1 contract

The deliverable is an OpenAPI 3.1 document the design maps onto directly: resources→`paths`, methods→operations, the envelope/error/entity shapes→`components/schemas`, reused responses/params→`components/responses`+`components/parameters` via `$ref`, auth→`components/securitySchemes`. Use 3.1 (full JSON Schema 2020-12: `type: ["string","null"]` for nullable, not the old `nullable`). Provide one worked contract per design and stop there — deep OpenAPI authoring, linting, mock servers, and SDK codegen are a separate concern. The full design→contract mapping plus a complete worked contract live in `references/openapi-mapping.md`.

## Rules

**Hard rules (never violate):**

- One error model for the whole API; **RFC 9457 problem+json is the default**, served as `application/problem+json`. Never mix two error shapes.
- Never return `200` (or any 2xx) with an error in the body. The status code is the contract.
- Resources are nouns; never put a verb in a path. Collections are plural and consistent.
- Every collection endpoint is paginated with an enforced max page size.
- Always HTTPS; auth is declared in the contract (`securitySchemes` + `security`), never implicit.
- PUT is full-replace, PATCH is partial; never conflate them.
- Use OpenAPI **3.1** (JSON Schema 2020-12) for the contract; express nullability with a `"null"` type member, not the removed 3.0 `nullable` keyword.

**Preferences (override-able):**

- Cursor/keyset pagination by default; offset only for small, stable, random-access datasets.
- URL-path versioning by default; major-version-only, additive changes never bump.
- Bearer/JWT for user APIs, API-key for service-to-service.
- `429` + `Retry-After` as the rate-limit baseline; add `X-RateLimit-*` advisory headers.
- Cap resource nesting at 2 levels; promote deeper children to top-level resources.

## Gotchas

- **PATCH treated as full replace** silently wipes fields the client didn't send. PATCH must merge only the provided fields; if you need replace semantics, use PUT.
- **200-with-error-body** looks fine in a browser but breaks retry logic, caches, and monitoring that key off status codes. Always set the real status.
- **Offset pagination drift:** under concurrent inserts/deletes, `?offset=` skips or repeats rows between pages, and deep offsets get progressively slower (the DB scans and discards every skipped row). Cursor/keyset avoids both.
- **422 vs 400 confusion:** returning 400 for a value that failed business validation (but parsed fine) loses information clients use to branch. Reserve 400 for "couldn't parse this at all."
- **`nullable: true` in an OpenAPI 3.1 schema** is silently ignored — it was a 3.0 keyword. Use `type: ["string", "null"]`. Validators won't always warn.
- **Idempotency assumed for POST:** clients (and proxies) may retry a timed-out POST, creating duplicates. If retries are expected, require an `Idempotency-Key` and dedupe server-side.
- **Leaking sequential internal IDs** (`/users/1001`) exposes row counts and enables enumeration. Use opaque IDs/UUIDs in the public surface.

## Anti-patterns

- "We'll just return 200 and put an `ok: false` in the body" — no. The status code is the machine-readable contract.
- "Verbs are clearer, so `/getUser` is fine" — no. The method is the verb; the path is the noun.
- "Two error formats, one per subsystem" — pick one (problem+json) and apply it everywhere.
- "Skip pagination, this collection is small" — collections grow; an unbounded list is a latent outage.
- "Version every endpoint independently / use minor versions in the URL" — version the whole API, major-only.
- "Re-teach FastAPI routing / Pydantic modeling here" — reference the `fastapi` and `pydantic-v2` skills; this skill owns the design, not the framework code.

## Output

This skill produces a **REST API design + its OpenAPI 3.1 contract**: a resource/URL map, a method-and-status-code decision per operation, the single error model (problem+json) and success/pagination envelope, the versioning/auth/rate-limit stance, and one worked OpenAPI 3.1 document expressing them. The abstract consumer is the engineer (or coding agent) who then implements the handlers — using the `fastapi` and `pydantic-v2` skills — and the downstream clients who integrate against the published contract.

## Related

- `fastapi` — framework mechanics (routers, dependency injection, `response_model`, exception handlers). This skill decides the contract; `fastapi` implements it.
- `pydantic-v2` — request/response schema modeling. This skill names the shapes; `pydantic-v2` models them.
- OpenAPI-authoring / SDK-codegen tooling — deeper contract authoring, linting, mock servers, and client generation (a separate concern this skill hands off to).
- `references/error-model.md`, `references/contract-patterns.md`, `references/openapi-mapping.md` — load triggers below.

## Progressive disclosure

Heavy content lives in `references/`, loaded only on demand:

- `references/error-model.md` — load when defining or fixing the error model: RFC 9457 member-by-member, the `errors` validation array, the `about:blank` default, a 404 and a 422 problem+json example, the FastAPI exception-handler pattern, and the non-standard `{error:{...}}` alternative for comparison.
- `references/contract-patterns.md` — load when shaping responses or pagination: the success envelope, cursor-vs-offset decision table with both response shapes, versioning lifecycle (Deprecation/Sunset/410), auth schemes, and rate-limit headers.
- `references/openapi-mapping.md` — load when expressing the design as a contract: the design→OpenAPI-3.1 element mapping, 3.1-vs-3.0 notes (JSON Schema 2020-12, null types, webhooks), and one complete worked contract with problem+json responses and a security scheme.
- `references/sources.md` — research provenance / citations.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap).
- Body ≤ ~500 lines / 5,000 tokens — kept in context every turn.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k tokens, error >50k.
