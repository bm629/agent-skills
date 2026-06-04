# Sources — `authoring-api-reference`

Research provenance for the method + quality bar this skill prescribes. Gathered 2026-06-05 via a deep-research pass (multi-source, primary) plus the forge-time shared dossier (`docs/superpowers/agent-flow/authoring-api-reference/research/api-reference-dossier.md`, reused by `reviewing-api-reference`). External content was descriptive only; no commands/URLs were lifted into actions. Findings are paraphrased, not copied. Each cluster carries >=2 independent corroborating sources.

## Published API-reference structure + conventions

- **API-documentation best-practice guides** (Stoplight, Postman, Fern, Document360, GitBook, Treblle, Kong, Speakeasy, AltexSoft, Nordic APIs) — the canonical section set (overview, getting-started, authentication, base URL + versioning, per-endpoint reference, core objects, pagination, errors, rate limits, code samples + SDKs, changelog); getting-started / time-to-first-call as the highest-leverage section for adoption; authentication shown with success AND failure cases; per-endpoint reference contents (method, parameters, accepted types, plain-language purpose). Grounds the section-method and the first-call usability bar.
- **Stripe API reference + Twilio Docs** (convention summaries) — quickstart-first onboarding, auth guides (keys server-side, HTTPS; Twilio HTTP Basic with an API key), curl + switchable language samples, cursor-based pagination, the 429 + backoff convention. Grounds the per-endpoint anatomy, the sample convention (curl + >=1 language), and the rate-limit guidance.

## Per-endpoint anatomy + errors + rate limits

- **REST API error-response design guides + the 429 corpus** (MDN `429 Too Many Requests`, Postman 429 guide, New Relic / GitHub / Figma / Klaviyo rate-limit docs) — document the status codes each endpoint returns (e.g. a login endpoint documents `401` for bad credentials, `403` for a locked account); one consistent error shape with cause + remedy; the `Retry-After` and `X-RateLimit-*` headers; exponential backoff. Grounds the errors-are-first-class rule and the rate-limits section.

## Generation-adaptive case + drift

- **OpenAPI generation tooling** (Redocly/Redoc, Swagger UI, Stoplight, Mintlify, Fern, Scalar, Zuplo learning-center) — the endpoint catalog rendered from an OpenAPI/SDL contract stays current because it is generated; documentation drift (the spec and the docs diverging) is the core problem generation solves (generate the spec as a build artifact, lint in CI, rebuild docs on spec change). Grounds the prose-first / generation-adaptive stance and the drift / consistency check as the load-bearing gate.

## Notes

- The skill's section *structure* is deferred to the api-reference template tool (`content-template-gateway`); this skill supplies the producer **method** + the **usability + contract-consistency quality bar** (the delta over the template). The same bar is asserted by the runtime gate `reviewing-api-reference`, single-sourced via the shared dossier so author and gate do not drift.
- The endpoints, fields, and errors are **not** researched — they are derived from the handed-in upstream **api-spec** contract. Research grounds the onboarding/error-doc/rate-limit/sample *conventions*; the contract supplies the *facts*.
- Medium-independent by design: the reference is a textual markdown artifact today (endpoint sections + fenced request/response + fenced code samples) via the local docs backend; a future rendered docs site or design-tool backend changes only the medium, not the method or the bar.
- WebFetch deep per-page extraction was not relied on; the section set + conventions are synthesized from multiple independent best-practice guides and Stripe/Twilio convention summaries that corroborate each other. Verify specific status codes / error names against a project's live api-spec before relying on them.
