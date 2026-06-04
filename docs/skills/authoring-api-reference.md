# authoring-api-reference

Author a **published, consumer-facing API reference** — the documentation an integrating client developer reads to call an API: an overview, a getting-started first-call walkthrough, an authentication walkthrough, base URL + versioning, a per-endpoint reference (purpose, typed parameters, a worked request + response example, the errors each returns), shared object types, an errors + rate-limits guide, copy-paste code samples, and a changelog. The how-to (a consumer-docs method + a usability/contract-consistency bar), composed with a separate api-reference template tool and a deep-research capability; targets a textual markdown artifact (endpoint sections + fenced request/response examples + fenced code samples).

## Purpose

An api-reference is the published consumer layer DERIVED FROM the engineering api-spec contract — distinct from it (the spec is the internal wire contract; the reference is the onboarding + worked examples a client developer integrates against). This skill carries the producer's judgment — not the section list — guiding a producer to derive every endpoint, field, and error from the upstream api-spec (never fabricating one), ground the onboarding narrative and examples in established public-API-docs practice, author prose-first by hand yet adapt where the catalog is generated from OpenAPI, and prove the reference stays consistent with the contract. The bar to clear: a developer can authenticate, make a first call, and integrate every operation from the reference alone, and every documented endpoint/shape/error traces to the api-spec with no drift.

## When to activate

- Authoring the published API reference for an API surface from its handed-in upstream api-spec (+ feature-spec / architecture-doc where present).
- Producing the getting-started + auth walkthrough, the per-endpoint reference with worked examples, shared types, an errors + rate-limits guide, and code samples.
- Filling an api-reference template with researched, contract-consistent, onboarding-first consumer content.

### When NOT to activate

- **The engineering wire contract** (the internal, exhaustive request/response/error spec) → `authoring-api-spec` (it is *upstream*; the reference is derived from and consistent with it).
- **The end-user product help** → `authoring-user-guide`; **the developer adoption/integration narrative** → `authoring-developer-guide` (which links this reference).
- **The implementation / persistence schema** → the design + data layers, not the published interface.
- **Reviewing a finished api-reference** → `reviewing-api-reference` (the paired acceptance gate).

## Workflow

Take the section structure from the api-reference template tool (don't invent an outline). Read the handed-in `depends_on` set — primarily the api-spec; derive every endpoint, parameter, shape, and error from it (never invent endpoints). Research to ground the reference in established public-API-docs practice (every endpoint has a working example; a getting-started + auth walkthrough leads; errors and rate-limits documented). Then fill each section to method: an overview + getting-started (the first successful call); the authentication walkthrough; base URL + versioning; the per-endpoint reference (per operation: purpose, typed parameters, a worked request + response example, its error responses + status codes); shared data types defined once; an errors + rate-limits guide; code samples (curl + at least one language, more where SDKs exist — not a fixed matrix); versioning/changelog + SDK pointers. Author prose-first; where the catalog is generated from OpenAPI, adapt to curating the generated output plus the surrounding narrative + the drift check. Surface any gap as an explicit assumption rather than fabricating. Self-check the consistency-against-the-contract before handoff.

## Output

A comprehensive API reference meeting the **usability + contract-consistency bar** (getting-started + auth let a developer make a first call; every api-spec operation documented with typed params + a worked example + its error responses; every endpoint/shape/error traces to the contract — no drift, nothing fabricated; code samples present; versioning stated). Textual markdown — the method and bar are medium-independent. Structure from the template; this skill supplies the content quality. The same bar the paired `reviewing-api-reference` gate asserts.

## Key guarantees

- **Composes, not duplicates** — defers structure to the template tool; supplies method + judgment.
- **Derived from the contract, no drift** — every endpoint/field/error traces to the upstream api-spec; nothing fabricated.
- **Onboarding-first** — getting-started + auth lead; every endpoint carries a worked request/response + its errors, not just the happy path.
- **Prose-first, generation-adaptive** — authored by hand by default; adapts to curating an OpenAPI-generated catalog plus the narrative and the drift check.
- **Single-sourced bar** — shared with `reviewing-api-reference`, so produce and review don't drift.

## License

MIT © 2026 Bhushan Modi.
