# reviewing-api-spec

Judge a **finished api-spec** — the engineering wire contract (operations, request/response schemas, auth, error model, pagination, versioning, examples) — and decide whether a client can call every operation and a server can implement it from the contract alone — an acceptance gate, not authoring. The review half of the api-spec pair; it single-sources its bar from the same conditions as `authoring-api-spec`, and is **style-agnostic** (REST / GraphQL / gRPC, no OpenAPI reflex).

## Purpose

An api-spec is the wire contract a client integrates against and a server implements. Before either happens, something has to decide whether the contract is complete enough to call and implement from — with no ambiguity about shapes, errors, or auth. This skill is that gate: it judges the contract against a **contract-completeness bar** and emits a machine-parseable verdict. The author's *techniques* (the style notation, the named RFCs, JSON-Schema fluency) are judged by **outcome** — but the complete error model, type-both-sides, and per-operation authorization are real load-bearing conditions: this IS the wire contract. The most-differentiating check from generic `design-review` is the **complete error model** (cond-5) — the single most-skipped part of an api-spec.

## When to activate

- ✅ A finished api-spec doc needs an accept/revise decision before a client integrates or a server implements.
- ✅ You are the independent reviewer / gate for an api-spec a producer just authored.
- ✅ Re-judging a revised api-spec after a prior `revise`, or reviewing an **amend** as a delta-scoped review.

### When NOT to activate

- **Authoring or repairing an api-spec** → `authoring-api-spec`.
- **Reviewing the data-model** (the stored entities the DTOs reference — upstream) or the **feature-spec** (upstream) → their own documents with their own gates.
- **Reviewing the published, consumer-facing api-reference** (the prose end-user docs, often generated *from* this contract — downstream) → `reviewing-api-reference`. This contract is that reference's source of truth, never the reverse.
- **Reviewing the implementation / server code** → this gate judges the *design document*, not code.
- **A generic / ad-hoc design doc, RFC, ADR, spec, or plan** → `design-review`. This gate is for the doc-library api-spec artifact (authoritatively the `template: api-spec` frontmatter; a `# API Specification` heading is a fallback only when frontmatter is absent).
- **Template/section conformance** → a template concern.

## The bar (12 conditions)

Detect the API style first, then judge each in its own idiom, pass/gap, proportional to the API: (1) **style, base & versioning** — the style, base, a versioning scheme + the breaking-vs-non-breaking rule + the deprecation→sunset policy; (2) **every operation listed & traced** to an upstream feature-spec behavior, correct method/success-status; (3) **every operation fully typed on both sides** + status codes — **a happy-path-only operation fails**; (4) **auth & per-operation authorization** — the scheme(s) + every non-public operation's required scope/role, no secret in a URL; (5) **error model complete** (signature) — one consistent error shape + every named failure case per operation with status + code + retryability; (6) **shared types defined once + referenced; reference-not-redefine the data-model**; (7) **pagination, filtering, sorting & rate-limits** — strategy + envelope + a stable tie-breaker + max page size; (8) **examples present + consistent** with the schemas; (9) **naming + versioning consistent** across the surface; (10) **grounded, honest & consistent** — no fabrication, one-directional vs the api-reference, references the data-model, consistent with the shipped API (`file:line`; greenfield clause — N/A when no API exists); (11) **(amend only) delta well-scoped, classified, ripple-clean, versioned** (n/a greenfield). A GraphQL contract legitimately has no HTTP status codes; a gRPC one uses `google.rpc.Status` — never revise for that.

## Output

Exactly `VERDICT: approve` or `VERDICT: revise` on its own line, plus findings. On `revise`, every finding is **actionable** — the failed condition, the exact location, and **how to fix it**. On `approve`, findings are optional non-blocking notes. **Approves** a contract a client can call + a server can implement (no false-revise on a thin API); **revises** only on a real, named callability/implementability gap.

## Key guarantees

- **Gate, not author** — judges and returns findings; never rewrites the contract.
- **Single-sourced bar** — the same 12 conditions the author produces to; no private stricter standard.
- **Style-agnostic, no OpenAPI reflex** — never revises a GraphQL/gRPC contract for lacking HTTP status codes / OpenAPI; judges its `errors`-array + nullability or `google.rpc.Status` + proto. The cardinal drift this gate guards against.
- **The error model is not the happy path** — an operation showing only its `2xx` is a real gap (a client can't write the `catch` branch).
- **One-directional vs the api-reference** — this contract is the published reference's source of truth, never reverse-engineered from it.
- **Greenfield consistency is N/A, not a gap** — absence of a deployed surface to verify is never itself a blocker.
- **capability-record-aware** — when a `capability_record` is injected by the authoring caller, judgment includes a capability-boundary condition (`entry_points`/`publishes`/`consumes`/`refs`); n/a when no record was injected.
- **Machine-parseable verdict** — the exact `VERDICT:` line a loop can read.

## License

MIT © 2026 Bhushan Modi.
