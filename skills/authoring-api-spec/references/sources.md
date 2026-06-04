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
- **REST API design + error-handling guides** (Postman, Speakeasy, Zuplo, Moesif; Stripe API docs as a canonical real-world example) — versioning (URL-path `/v1` least ambiguous; plan from the start), auth (OAuth 2.0 + PKCE, JWT, API keys, HTTPS), the consistent error body (machine code + message + request id), pagination (cursor vs offset; Stripe `starting_after`/`ending_before`; `Link` header; `has_more`), and rate-limit headers (`RateLimit-*`, `Retry-After`). Grounds the versioning, auth, error-model, and pagination/rate-limit sections.

## Notes

- Style-agnostic by design: a project picks one style; the per-operation and shared-type sections render in that style's notation (OpenAPI fragment / SDL / proto). The section set and the quality bar are common across styles and medium-independent (the contract is expressed textually in markdown today).
- The skill's structure is deferred to the api-spec template tool; this skill supplies the producer method + the no-ambiguity quality bar (the delta over the template).
