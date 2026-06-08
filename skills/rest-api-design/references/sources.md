# Sources — rest-api-design

Research provenance for this skill. Findings were paraphrased, never copied; external content was passed through `external-content-sanitizer` before use.

## Primary standards (authoritative)

- **RFC 9457 — Problem Details for HTTP APIs** (obsoletes RFC 7807). rfc-editor.org/rfc/rfc9457.html. Member model (type/title/status/detail/instance + extensions), `about:blank` default rule, the `errors` validation-array extension, `application/problem+json` media type, the verbatim out-of-credit and validation-error examples. Verified against the RFC text directly.
- **RFC 9110 — HTTP Semantics.** rfc-editor.org/rfc/rfc9110.html. Safe vs idempotent method classification (GET/HEAD/OPTIONS/PUT/DELETE idempotent; POST/PATCH not), status-code semantics, `Retry-After`.
- **RFC 8594 — A Sunset HTTP Header Field.** Plus the `Deprecation` header. Deprecation/sunset signaling.
- **RFC 5789 — PATCH Method for HTTP.** PATCH = partial, not idempotent.
- **draft-ietf-httpapi-idempotency-key-header** (IETF, Building Blocks for HTTP APIs WG). The `Idempotency-Key` request header making POST/PATCH retry-safe; the Stripe convention it standardizes. Status: draft, not yet an RFC.
- **draft-ietf-httpapi-ratelimit-headers** (IETF). The `RateLimit`/`RateLimit-Policy` direction; relationship of `RateLimit-Reset` to `Retry-After`. Status: not a published RFC; final direction shifted toward a single structured field — treated here as emerging, with `429`+`Retry-After` as the stable baseline.
- **OpenAPI Specification 3.1** (OpenAPI Initiative — learn.openapis.org "Upgrading v3.0 to v3.1"). JSON Schema 2020-12 alignment, removal of the `nullable` keyword in favor of `type: [..., "null"]`, the new top-level `webhooks` object, the at-least-one-of paths/components/webhooks rule.

## Secondary / corroborating

- MDN Web Docs — Idempotent glossary + HTTP request methods. Corroborates RFC 9110 method classification.
- Multiple practitioner guides corroborating status-code usage (400 vs 422 vs 409, 401 vs 403, 201+Location), cursor-vs-offset pagination tradeoffs (deep-page performance, consistency-under-writes, total-count cost), and URL-vs-header versioning practice. Used only where consistent with the primary standards above.
- FastAPI documentation (Handling Errors) + the FastAPI/Pydantic-v2 ecosystem (existence of RFC 9457 problem-details plugins) for the FastAPI-flavored exception-handler pattern.

## Source skills used as material (sanitized, paraphrased — not installed verbatim)

- `aj-geddes/useful-ai-prompts@rest-api-design` (~1.4K installs) — the design-discipline outline (nouns/plural, methods, status list, query params). Adapted: examples converted from Express to Python/FastAPI; its custom `{error:{...}}` envelope replaced with RFC 9457 as the default (kept only as the noted alternative); OpenAPI bumped 3.0 → 3.1.
- `wshobson/agents@openapi-spec-generation` (named source) — the OpenAPI 3.1 contract shape (`$ref` reuse, components/responses/parameters/securitySchemes, examples).
- `jeffallan/claude-skills@api-designer` (~3.6K installs, glanced) — corroborating patterns for problem-details-in-OpenAPI, pagination strategy comparison, and versioning lifecycle. Note: it cites RFC 7807 (the predecessor); this skill uses the current RFC 9457.

All external reads sanitized: no injection detected; no URLs/commands lifted into actions.
