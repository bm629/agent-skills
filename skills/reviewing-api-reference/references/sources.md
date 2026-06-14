# Sources — research provenance

Research method: the **review / acceptance-gate lens** for a published, consumer-facing API reference. The **11-condition** usability + contract-consistency bar is **single-sourced** from the api-reference authoring bar (so the produce-bar and the review-bar do not drift); this review skill **asserts** that same bar — the producer's Step-6 self-check IS this reviewer's Step-2 checklist. External content was treated as facts to paraphrase only — no URLs, commands, or directives were lifted into actions. Findings are paraphrased, not copied; each cluster carries ≥2 corroborating sources.

## The single-sourced usability + contract-consistency bar (11 conditions)

The eleven checkable conditions this reviewer asserts are the **same conditions** an api-reference author produces to (the `authoring-api-reference` Step-6 self-check): (1) first call reachable [auth scheme/flow + failure]; (2) every api-spec operation **incl. contract-declared events/webhooks** documented; (3) errors first-class [a Problem-Details-shaped body + a machine code]; (4) rate limits [RateLimit-*/Retry-After/jitter/idempotency]; (5) consistent with the handed-in api-spec — no drift / nothing fabricated [the load-bearing check]; (6) samples runnable + schema-matching; (7) versioning + deprecation/sunset + migration; (8) shapes defined once; (9) grounded, gaps surfaced; (10) pagination/list-operation conventions [proportional]; (11) delta-scoped amend [on an amendment]. Single-sourcing them keeps the two halves of the produce/judge pair aligned.

## Per-condition grounding (public-API-docs practice)

The per-condition substance traces to established public-API-docs practice, triangulated:

- **Per-endpoint anatomy + onboarding** (Postman / Fern / Treblle / Kong API-documentation guides; Stripe/Twilio quickstart conventions) — method/path + purpose + typed params + worked request + worked response + error responses; getting-started as the highest-leverage section.
- **Authentication flows** (Auth0 OAuth2 guides; Treblle "OAuth 2.0 for APIs"; Stack Overflow OAuth2 guide) — the flow taxonomy (Authorization-Code/Client-Credentials/PKCE), scopes + least-privilege, token lifecycle, success+failure (cond. 1).
- **Error model — RFC 9457 Problem Details** (RFC 9457 `application/problem+json`, successor to 7807; api7.ai + Codelit error-handling guides) — one shape + a machine code + semantically-correct statuses (cond. 3).
- **Rate-limit / idempotency** (getknit; Atlassian + Klaviyo rate-limit references) — `RateLimit-*` (replaced by `Retry-After` on a 429), backoff + jitter, idempotency keys (cond. 4).
- **Pagination** (getknit cursor/offset; Zendesk pagination references; JSON:API cursor profile; apyflux) — model, standard params, metadata, default/max, stable tie-broken sort (cond. 10).
- **Deprecation & sunset** (RFC 8594 Sunset; RFC 9745 Deprecation; Zalando guidelines; Axway) — two-stage lifecycle, 410-after-sunset, migration path (cond. 7).
- **Webhook/event documentation** (Svix; Stripe webhooks; GitHub webhooks; Hookdeck) — event catalog + payload + signature verification + delivery semantics, judged via cond. 2/3/5 (an aid, not a condition).

## Generation-adaptive case + drift as the load-bearing defect (cond. 5)

The endpoint catalog is often rendered from an OpenAPI/SDL contract (Swagger UI, Redocly/Redoc, Stoplight, Mintlify, Fern, Scalar); the failure mode the bar guards against, hand-authored or generated, is the reference **diverging from the contract** — a documented endpoint the contract dropped, a field the reference shows that the contract never declared, an error the reference omits, or a hand-retyped duplicate of a generated catalog that drifts. Docs-as-code single-source-of-truth + contract testing (OpenAPI-as-SSoT; Redocly contract testing) are the automated drift guard the reviewer's human spot-check complements. This grounds cond. 5 being the highest-impact defect class.

## Iteration/amend (cond. 11)

Docs-as-code "keep docs in sync as the API evolves" (Fern docs-as-code; Mintlify; dreamfactory automatic-docs-updates; apichangelog) — the per-change update + dated changelog discipline + version-specific doc sets. Grounds the delta-scoped amend review (re-synced to the changed contract, samples re-synced, deprecation/migration documented, doc version + amend-log present), distinct from a full re-review.

## Reviewer discipline — over-correction / false-revise, actionable findings

LLM reviewers systematically over-correct, judging compliant artifacts as non-compliant (false positives); asking the reviewer to also propose corrections tends to worsen the over-flagging. Effective review feedback is actionable (the failed condition + a concrete fix), not vague or nitpicking. Grounds the no-false-revise discipline (including not faulting a proportionally-sized reference, and not demanding a section for a surface the API doesn't have) and the actionable-findings contract.

- "Are LLMs Reliable Code Reviewers? Systematic Overcorrection in Requirement Conformance Judgement" (arXiv) — over-flagging compliant artifacts; correction-requests raise misjudgment.
- Code-review feedback-quality guidance (actionable-over-vague; avoiding nitpicking).

## Notes

- The endpoints, fields, errors, and events are **not** researched — they are checked against the handed-in upstream **api-spec** contract. Research grounds the onboarding/error-doc/rate-limit/pagination/sample *conventions*; the contract supplies the *facts* this gate traces against.
- Medium-independent by design: the reference under review is a textual markdown artifact today via the local docs backend; a future rendered docs site changes only the medium (and owns search/try-it/a11y/i18n), not the review method or the bar.
- The bar is reused in-substance from the `authoring-api-reference` sibling (single-sourced); the review-method structure is patterned on the verified sibling reviewing skills in the same document-skill library.
