# Sources — `authoring-api-spec`

Research provenance for the method + quality bar this skill prescribes. Gathered 2026-06-04 via a deep-research pass (multi-source, primary) plus the forge-time dossier. External content was descriptive only; no commands/URLs were lifted into actions. Findings are paraphrased, not copied.

## API interface-definition standards (the three styles)

- **OpenAPI Specification v3.x** (spec.openapis.org; swagger.io/specification) — the REST contract structure: Paths (endpoints + operations), parameters, requestBody, responses keyed by HTTP status, reusable `components.schemas`, and `securitySchemes`. Grounds the per-operation request/response, shared-types, and auth sections for REST.
- **JSON Schema** (json-schema.org) — field types, `required`, and constraints (length, enum, format, range). Grounds the "fully typed, required/optional, constrained" rule.
- **GraphQL schema / SDL** (graphql.org/learn/schema; Apollo Server docs) — typed object/scalar/enum/input types, the `Query`/`Mutation`/`Subscription` root operation types, and the `data`-vs-`errors` response shape. Grounds the GraphQL flavor.
- **gRPC core concepts + Protocol Buffers** (grpc.io/docs; protobuf.dev) — `service`/`rpc` method definitions, typed request/response `message`s, the four method kinds, and status codes. Grounds the RPC flavor.

## HTTP + error + design conventions

- **RFC 9110 — HTTP Semantics** (rfc-editor.org) — status-code semantics (2xx/4xx/5xx) underpinning the response + error sections.
- **RFC 9457 — Problem Details for HTTP APIs** (rfc-editor.org) — the recommended REST error response shape (`type`, `title`, `status`, `detail`, `instance`; `application/problem+json`); successor to RFC 7807. Grounds the "one consistent error shape" rule.
- **REST API design + error-handling guides** (Postman, Speakeasy, Zuplo, Moesif; Stripe API docs as a canonical real-world example) — auth (OAuth 2.0 + PKCE, JWT, API keys, HTTPS), the consistent error body (machine code + message + request id), pagination (cursor vs offset; Stripe `starting_after`/`ending_before`; `Link` header; `has_more`), and rate-limit headers (`RateLimit-*`, `Retry-After`). Grounds the auth, error-model, and pagination/rate-limit sections.

## Versioning & evolution standards

- **RFC 8594 — The Sunset HTTP Header Field** + **RFC 9745 — The Deprecation HTTP Response Header Field** (rfc-editor.org) — the two-stage retirement lifecycle: `Deprecation` (value = an RFC 9651 Date) → a migration window → `Sunset` (an HTTP-date; `Sunset` ≥ `Deprecation`). Grounds the deprecation→sunset policy + the amend method.
- **Google AIP-180 (backwards compatibility) + AIP-185 (versioning)** (google.aip.dev) — the source/wire/semantic compatibility framing (additive = safe; removal/rename/narrowing/required-add = breaking) + major-version-only numbering. Grounds the breaking-vs-non-breaking classification.
- **OpenAPI 3.1 / 3.2** (spec.openapis.org) — JSON-Schema-2020-12 alignment; the `deprecated` flag; `securitySchemes` incl. the device-authorization flow. Grounds the typed-schema + deprecation-marker rigor.
- **Relay GraphQL Cursor Connections Specification** (relay.dev/graphql/connections.htm) — `edges`/`pageInfo` (`hasNextPage`/`hasPreviousPage` non-null; `startCursor`/`endCursor` opaque). Grounds GraphQL pagination.
- **IETF RateLimit header fields** (`draft-ietf-httpapi-ratelimit-headers`, RFC 9651 structured fields) — the structured `RateLimit` + `RateLimit-Policy` fields; **still a draft** (not yet an RFC); the legacy `RateLimit-Limit`/`-Remaining`/`-Reset` convention remains widely deployed. State the chosen convention; don't assert the draft is an RFC.

## Notes

- Style-agnostic by design: a project picks one style; the per-operation and shared-type sections render in that style's notation (OpenAPI fragment / SDL / proto). The section set and the quality bar are common across styles and medium-independent (the contract is expressed textually in markdown today).
- The skill's structure is deferred to the api-spec template tool; this skill supplies the producer method + the no-ambiguity quality bar (the delta over the template).
