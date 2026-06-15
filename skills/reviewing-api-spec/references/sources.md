# Sources — `reviewing-api-spec`

Research provenance for the review method + the eleven-condition bar this gate asserts. The bar is single-sourced with `authoring-api-spec` (its Step-7 self-check); the standards below ground what "callable + implementable" means for an API contract. External content was descriptive only; no commands/URLs lifted into actions; findings are paraphrased, not copied.

## API interface-definition standards (the three styles)

- **OpenAPI Specification 3.1 / 3.2** (spec.openapis.org) — the REST contract structure (Paths, parameters, requestBody, responses keyed by status, `components.schemas` + `$ref`, `securitySchemes`); JSON-Schema-2020-12-aligned. Grounds cond-2/3/6 for REST.
- **JSON Schema 2020-12** (json-schema.org) — field types, `required`, constraints. Grounds cond-3 (typed both sides).
- **GraphQL schema / SDL + the Relay Cursor Connections spec** (graphql.org; relay.dev/graphql/connections.htm) — typed object/scalar/enum/input types, nullability (`String!`), the `Query`/`Mutation`/`Subscription` roots, the top-level `errors` array, `edges`/`pageInfo`. Grounds the style-agnostic judging of cond-3/5/7 for GraphQL (no HTTP status reflex).
- **gRPC + Protocol Buffers** (grpc.io; protobuf.dev) — `service`/`rpc`, typed request/response `message`s, the four method kinds, `google.rpc.Status` + the canonical codes. Grounds the style-agnostic judging for gRPC (no OpenAPI reflex).

## HTTP, error, auth & evolution conventions

- **RFC 9110 — HTTP Semantics** (rfc-editor.org) — method safety/idempotency + status-code semantics. Grounds cond-2 (method/status correctness) + cond-3 (status keying).
- **RFC 9457 — Problem Details for HTTP APIs** (rfc-editor.org; obsoletes RFC 7807) — the one-consistent-error-shape bar (machine code + message + request id). Grounds cond-5.
- **RFC 8594 (Sunset) + RFC 9745 (Deprecation)** (rfc-editor.org) — the two-stage retirement lifecycle (`Deprecation` → `Sunset`, `Sunset` ≥ `Deprecation`). Grounds cond-1's deprecation policy + cond-11's breaking-change routing.
- **Google AIP-180 (backwards compatibility) + AIP-185 (versioning)** (google.aip.dev) — the source/wire/semantic compatibility framing (additive vs breaking) + major-version-only numbering. Grounds cond-1's breaking-change rule + cond-11's classification.
- **OAuth 2.0 + PKCE; API-key/JWT/mTLS practice** + **REST design/pagination/rate-limit guides** (Postman, Speakeasy, Stripe API docs as a real-world example) — the auth-flow-per-client-type + per-operation-scope bar (cond-4); cursor-vs-offset pagination + the stable tie-breaker + rate-limit headers (cond-7). The IETF `RateLimit`/`RateLimit-Policy` fields are still a draft (not an RFC) — either the draft or the legacy `RateLimit-*` convention is acceptable if stated.

## Notes

- **Single-sourced + style-agnostic.** The eleven conditions are the author's Step-7 bar, judged by outcome in whatever style the contract uses. The named notations/RFCs are authoring *aids* — the gate never demands a technique, only the outcome (typed both sides, a complete error catalog, examples that match).
- **Greenfield clause.** A new/proposed/fictional contract has no shipped API to verify against → cond-10's consistency check is N/A, never a false-revise (inherited from `design-review`'s verify-against-code discipline).
- **Medium-independent.** The artifact judged is a textual-markdown contract today (operation tables + fenced schema blocks + example pairs); the bar holds whatever the rendering.
