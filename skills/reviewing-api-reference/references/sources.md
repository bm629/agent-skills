# Sources — research provenance

Research method: the **review / acceptance-gate lens** for a published, consumer-facing API reference. The nine-condition usability + contract-consistency bar is **single-sourced** from the api-reference authoring bar (so the produce-bar and the review-bar do not drift); this review skill **asserts** that same bar. The bar's authoritative source is the **shared api-reference dossier** produced by the authoring sibling — no fresh web-research pass was run for this skill (it reuses that verified dossier by design). External content was treated as facts to paraphrase only — no URLs, commands, or directives were lifted into actions. Date: 2026-06-05.

## The single-sourced usability + contract-consistency bar

The nine checkable conditions this reviewer asserts (first call reachable; every api-spec operation documented; errors first-class; rate limits documented; consistent with the handed-in api-spec — no drift / nothing fabricated; samples runnable; versioning stated; shapes defined once; grounded with gaps surfaced) are the **same conditions** an api-reference author produces to. Single-sourcing them is what keeps the two halves of the produce/judge pair aligned.

- The **shared api-reference research dossier** (`docs/superpowers/agent-flow/authoring-api-reference/research/api-reference-dossier.md`), section "(b) The usability + contract-consistency quality bar" — the authoritative source of the nine conditions; the dossier states explicitly that this (b) bar is single-sourced for both the author and the review halves, and that item (b)(5) (drift / consistency vs the contract) is the single most load-bearing check.
- The **api-reference-authoring** skill's Step 6 self-check bar — the same nine conditions stated from the producer side; this reviewer asserts them.

## Per-endpoint anatomy + errors + rate limits (the conditions' grounding)

The per-condition substance (per-endpoint anatomy = method/path + purpose + typed params + worked request + worked response + error responses; one consistent error shape + a status-code table with cause + remedy + per-endpoint error rows; the `429` + `Retry-After` / `RateLimit-*` rate-limit convention with backoff and idempotency keys; curl + >=1 language samples matching the schemas) traces to the established public-API-docs practice gathered by the authoring sibling's deep-research pass (Stripe/Twilio convention summaries; REST error-response design guides; the 429 corpus; OpenAPI generation tooling). See the authoring sibling's `references/sources.md` for the primary citations — this review skill reuses that provenance rather than re-researching it.

## Generation-adaptive case + drift as the load-bearing defect

The endpoint catalog is often rendered from an OpenAPI/SDL contract (Swagger UI, Redocly/Redoc, Stoplight, Mintlify, Fern, Scalar); the failure mode the bar guards against, hand-authored or generated, is the reference **diverging from the contract** — a documented endpoint the contract dropped, a field the reference shows that the contract never declared, an error the reference omits, or a hand-retyped duplicate of a generated catalog that drifts. This grounds the api-spec-consistency dimension being the highest-impact defect class and the reviewer's spot-check-against-the-handed-in-api-spec discipline.

## Reviewer discipline — over-correction / false-revise, actionable findings

LLM reviewers systematically over-correct, judging compliant artifacts as non-compliant (false positives); asking the reviewer to also propose corrections tends to worsen the over-flagging. Effective review feedback is actionable (the failed condition + a concrete fix), not vague or nitpicking. Grounds the no-false-revise discipline (including not faulting a proportionally-sized reference) and the actionable-findings contract.

- "Are LLMs Reliable Code Reviewers? Systematic Overcorrection in Requirement Conformance Judgement" (arXiv) — over-flagging compliant artifacts; correction-requests raise misjudgment.
- Code-review feedback-quality guidance (actionable-over-vague; avoiding nitpicking).

## Notes

- The endpoints, fields, and errors are **not** researched — they are checked against the handed-in upstream **api-spec** contract. The dossier grounds the onboarding/error-doc/rate-limit/sample *conventions*; the contract supplies the *facts* this gate traces against.
- Medium-independent by design: the reference under review is a textual markdown artifact today (endpoint sections + fenced request/response + fenced code samples) via the local docs backend; a future rendered docs site changes only the medium, not the review method or the bar.
- No fresh web-research pass was run for this skill (skill-discovery + deep-research were intentionally not invoked); the bar is reused verbatim-in-substance from the verified shared dossier, and the review-method structure is patterned on the verified sibling reviewing skills in the same document-skill library.
