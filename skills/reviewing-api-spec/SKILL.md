---
name: reviewing-api-spec
description: >
  Use when reviewing/judging a finished api-spec — the engineering wire contract
  (operations, request/response schemas, auth, error model, pagination,
  versioning, examples) — to decide if a client can call every operation and a
  server can implement it from the contract alone. An acceptance gate, not
  authoring. Judges a single-sourced 11-condition contract-completeness bar:
  style + base + versioning + deprecation policy; every operation listed +
  traced; every operation fully typed both sides + status codes (happy-path-only
  fails); auth + per-operation authorization; a complete error model (one shape +
  every failure case + retryability); shared types referencing the data-model;
  pagination + a tie-breaker; examples matching the schemas; one-directional vs
  the api-reference; consistent with the shipped API; delta-scoped amend.
  Style-agnostic (REST/GraphQL/gRPC, no OpenAPI reflex). Emits exactly
  `VERDICT: approve|revise`. Not authoring, the data-model, the api-reference, or
  generic design docs (design-review).
extensions:
  claude:
    when_to_use: "judging a finished api-spec doc (greenfield or an amend) against the contract-completeness bar and emitting an approve/revise verdict"
    argument-hint: "<the finished api-spec doc to review, or the amended contract + its change request>"
version: "1.1.0"
forge:
  status: reviewed
  forged: 2026-06-15
  reviewed: 2026-06-15
---

# `reviewing-api-spec` — SKILL.md

> **Variant:** standard · **When to use:** judging a finished api-spec document as an acceptance gate — checking a client can call every operation and a server can implement it from the contract alone, then emitting `VERDICT: approve|revise` with actionable findings. Greenfield, or an amend (delta-scoped).

## Overview

This skill is the *review* half of a producing/judging api-spec pair. Loaded by a reviewer who holds a **finished api-spec document** — the engineering **wire contract** of an API surface (operations, request + response schemas, auth, the error model, pagination/rate-limits, versioning, examples) — it judges that doc against one question: **can a client engineer call every operation correctly and a server engineer implement it, from this document alone, with no ambiguity about shapes, errors, or auth?** It applies a fixed **11-condition contract-completeness checklist** — the same bar an api-spec author produces to (`authoring-api-spec`'s Step-7 self-check), so the produce-bar and the review-bar do not drift — then emits a single machine-parseable verdict plus findings the author can act on in one revision pass. It is an acceptance gate — it does **not** author, fix, or rewrite the contract; it judges and returns findings, and the producer revises.

The bar is **single-sourced** with the author. The author's *techniques* — the style notation (OpenAPI / GraphQL SDL / proto), the named RFC conventions (RFC 9457, RFC 8594/9745, AIP-180/185), JSON-Schema fluency — are **aids the reviewer judges by OUTCOME** (is every operation typed both sides? is there one consistent error shape with every failure case named? do the examples match the schemas?), never conditions to demand. **But note the boundary:** the **complete error model** (cond-5), **type-both-sides** (cond-3), and **per-operation authorization** (cond-4) ARE real, load-bearing conditions for an api-spec — this IS the wire contract, so do NOT under-review them as "implementation detail." What stays an aid is the *technique* (a named notation/RFC), not the *outcome* (a typed operation, a complete error catalog, a per-operation scope).

**Style-agnostic (load-bearing).** The contract may be REST (OpenAPI/JSON-Schema), GraphQL (SDL + the `errors` array + nullability), or RPC/gRPC (proto + `google.rpc.Status`). Judge each in its own idiom: a GraphQL contract legitimately has **no HTTP status codes** (errors travel in the `errors` array; the typed payload-or-errors is the response), and a gRPC contract uses `google.rpc.Status` + the canonical codes, not HTTP. Demanding REST/OpenAPI idioms of a non-REST contract is the cardinal **OpenAPI-reflex false-revise** — do not do it. The style-agnostic guard threads cond-2 (operations), cond-3 (typed both sides), and cond-5 (error model): judge those *in whatever style the contract uses*.

## When to activate

- A finished api-spec doc needs an accept/revise decision before a client integrates or a server implements.
- You are the independent reviewer / gate for an api-spec a producer just authored.
- Re-judging a revised api-spec after a prior `revise` verdict.
- Reviewing an **amend** — an approved contract + a change request — as a delta-scoped review (cond-11).

**Do NOT activate when:**

- Authoring or repairing an api-spec → use `authoring-api-spec`. This skill never writes the contract.
- Reviewing the **data-model** (the stored entities the wire DTOs reference — *upstream*, one-directional) or the **feature-spec** (what the features do — *upstream*) → those are their own documents with their own gates.
- Reviewing the published, consumer-facing **api-reference** (the prose end-user docs, often generated *from* this contract — *downstream*) → use `reviewing-api-reference`. This contract is that reference's source of truth, never the reverse.
- Reviewing the **implementation / server code** that fulfils the contract → this gate judges the *design document*, not code.
- Reviewing a **generic / ad-hoc engineering design doc, RFC, ADR, spec, or plan** → use `design-review`. **This** gate is for the doc-library api-spec artifact — identified **authoritatively** by the `template: api-spec` frontmatter; a `# API Specification` heading is a fallback signal only when frontmatter is absent.
- Checking template/section conformance → that is a template concern. This skill judges *quality against the bar*, not whether every heading is present.

## Workflow

### Step 1: Read the whole contract with fresh, independent eyes

Read the api-spec doc end to end as if encountering it for the first time. Your stance is a gatekeeper for the *next* step (a client integrating + a server implementing): a finding carries weight only when it shows the API cannot be **called or implemented as designed**. Keep the upstream **feature-spec** (+ data-model where given) at hand — cond-2/cond-6/cond-10 check the contract against them. **Detect the API style first** (REST / GraphQL / gRPC, possibly mixed) so you judge each in its own idiom. **The input is the doc itself** — the operation list + the per-operation schemas + the error catalog + the shared types + the auth section + the examples all live in it (template sections); no separate companion artifact is required. **Is this an amend?** If you were handed a change request / delta against an existing contract, run the delta-scoped path (cond-11 active; scope to the changed operations + their classification + the deprecation/ripple). On a greenfield first build no change request is present — cond-11 is n/a.

### Step 2: Run the contract-completeness checklist — judge each condition

For each condition, decide **pass** or **gap**. A condition fails only on a *real, named* deficiency — "I'd have designed it differently" is not a gap. The conditions are the single-sourced bar; do not add private ones.

The capability-boundary checklist item (below) applies ONLY when a `capability_record` was injected into the authoring invocation and is available as review context. When absent, treat it as n/a — do not penalise a document for lacking capability-boundary markers when no boundary was defined.

1. **Style, base & versioning.** The API style, base URL/endpoint, and a concrete versioning scheme are present; the **breaking-vs-non-breaking change rule + the deprecation→sunset policy** are stated. *Gap* on a missing versioning scheme, or no breaking-change rule / no deprecation policy. *(Collapse: a v1 greenfield API states the policy even if nothing is deprecated yet. Non-collapsing baseline — style + base + a versioning scheme are present at any size.)*
2. **Every operation listed & traced.** The operation list is complete + scannable; each operation maps to an upstream feature-spec behavior (no orphan/invented endpoint, none missing); the method + success-status semantics are correct (a mutating `GET`, or `200` where `201` belongs, is a gap). *Gap* on an operation with no trace (an invented endpoint), a feature-spec behavior with no operation, or a wrong method/status. *(Judged against the upstreams given — an absent feature-spec is never itself a revise trigger.)*
3. **Every operation fully typed on both sides.** Request + response fully typed, each field required/optional with constraints, every response keyed to a status code (REST) / a typed payload-or-`errors` (GraphQL) / a typed response message (gRPC). *Gap* on an untyped/unconstrained field, or a response with no status/typed body. **A happy-path-only operation (only its `2xx`) fails.** *(Part of the signature spine; non-collapsing baseline — every operation is typed both sides at any size.)*
4. **Auth & per-operation authorization.** The authentication scheme(s) + credential location named; the OAuth flow chosen per client type; **every non-public operation names its required scope/role** (mapped to the op list); token lifecycle + HTTPS + no-secret-in-a-URL. *Gap* on an operation with no stated authorization (silently open or "logged-in" with no scope), an unnamed scheme, or a credential in a URL. *(Collapse: an all-public API has no per-op scopes — but the scheme/transport are still stated.)*
5. **Error model complete.** **One consistent error shape** for the whole API (a machine code + a message + a request/trace id), AND **every named failure case enumerated per operation** (validation/`401`/`403`/`404`/`409`/`429`/`5xx` as applicable) with its status + code + **retryability**. *Gap* on an operation showing only its `2xx`, an ad-hoc/different error body per endpoint, a missing machine code/request id, or no retryability. **The signature condition — the one that most differentiates this from generic `design-review`.** *(Non-collapsing baseline — the error model is not just the happy path at any size; a read-only op still names its `401`/`404`.)*
6. **Shared types defined once + referenced; reference-not-redefine the data-model.** Reusable DTOs defined once and referenced (no inline re-typing/drift); wire DTOs **reference the data-model + note the deltas**, never restate/contradict it. *Gap* on the same shape re-typed inline across operations (drift risk), or a DTO that re-types & contradicts a handed-in data-model. *(Part of the signature spine. Greenfield clause: no data-model handed in → the DTO stands alone, not a gap.)*
7. **Pagination, filtering, sorting & rate-limits.** Collection operations define pagination (strategy + envelope + default/max page size); filterable/sortable fields + a **stable tie-breaker**; rate limits + headers + `429`. *Gap* on an unpaginated/unbounded collection, a sorted-paginated collection with no tie-breaker, or a missing max page size. *(Collapse: a non-collection / single-resource API has no pagination — never false-revise it for "no pagination".)*
8. **Examples present + consistent.** ≥1 worked request/response pair per primary operation, **consistent with the schemas** (same field names, types, status codes, error shape). *Gap* on an example with a field the schema lacks, a wrong type, a wrong status, or an error body that isn't the shared shape. *(The api-spec analog of diagram⇄tables sync. Collapse: examples for the primary operations, not necessarily every one.)*
9. **Naming + versioning consistent.** The naming convention + the versioning scheme are applied **uniformly across the surface** (no operation deviating). *Gap* on inconsistent naming/casing or a versioning scheme applied unevenly. *(Scoped to surface-**uniformity** — distinct from cond-1's *presence of the policy* and cond-2's *per-operation correctness*; do not re-litigate those here.)*
10. **Grounded, honest & consistent.** Operations/shapes/limits/codes reflect the feature-spec + data-model (not invented/boilerplate); assumptions explicit (thin-input → a blocker, not an invented shape); **no fabrication**; **one-directional vs the api-reference** (this contract is the published reference's source of truth — not reverse-engineered from the api-reference); **references the data-model** (one-directional, upstream); **consistent with the shipped API** where one exists (claims about current operations/shapes verified `file:line`, marked unverified where unconfirmable). *Gap* on an invented field/limit/status/code, an operation reverse-engineered from the published reference, or a documented operation that contradicts the deployed surface. *(Non-collapsing baselines — no-fabrication + one-directional hold at any size. **Greenfield clause:** a brand-new/proposed/fictional API has no shipped surface → the consistency check is **N/A**, never a false-revise.)*
11. **(Amend only) delta is well-scoped, classified, ripple-clean, versioned.** When reviewing a change against an existing contract: the changed operations meet conditions 1–10 **on what they touched**; the change is **classified additive/breaking**; a **breaking change carries a new version + the deprecation→sunset plan + a migration guide** (not an in-place edit under the same version); backward/forward compatibility analyzed; the **forward/downward ripple** flagged (the downstream api-reference re-sync, the impl/test-plan, the live clients); the doc version bumped + a changelog present; retired operations marked deprecated, not silently deleted. *Gap* on an un-scoped delta, a breaking change mis-classified as additive (or edited in place under the same version), an un-flagged ripple, or a silent deletion. *(Collapse: on a greenfield first build this condition is n/a — do NOT full-re-review an unchanged contract, and do NOT demand a changelog on a first draft.)*

12. **Capability boundary (n/a when no capability_record):** all `entry_points` reachable as API operations; `publishes`/`consumes` events have corresponding async operations; `refs` fields marked read-only cross-capability.

**Proportionality.** "Callable + implementable" scales with the API. A thin API legitimately collapses what it does not need — one operation → a short list; no collections → no pagination; an all-public read API → no per-op scopes; a greenfield contract → no shipped API to verify against; a first draft → no changelog. Judge **completeness of the contract decisions**, not word count or template-section presence. A small, complete contract that satisfies every *applicable* condition **passes**. Do not manufacture a gap from brevity.

### Step 3: Decide the verdict

- **approve** — every applicable condition passes. A client can call every operation and a server can implement it from the contract alone, with no ambiguity about shapes, errors, or auth. Approve even if you can imagine stylistic improvements; the bar is callability + implementability, not perfection.
- **revise** — one or more conditions have a real, named gap that blocks calling or implementing (a happy-path-only operation, an untyped field, an inconsistent/missing error catalog, an example that contradicts its schema, a DTO that contradicts the data-model, an operation with no authorization, a breaking change edited in place, an un-scoped amend, etc.).

Do not revise to signal effort or to request nice-to-haves. A condition is either met or it isn't.

### Step 4: Emit the verdict + actionable findings

Emit the verdict as a single line — the literal text `VERDICT: approve` or `VERDICT: revise`, on its own line, with **no** surrounding code fences, quotes, or extra words (the fences here are illustration only):

```
VERDICT: approve
```

Then, on the following lines, list findings. On `revise`, every finding is **actionable** — the failed condition, the exact location, and **how to fix it** — so the author can resolve it in one pass. On `approve`, findings are optional non-blocking notes.

A good finding names the gap and the fix:

> **revise** — Error model complete (cond. 5), §3 `GET /invoices`: the operation documents only its `200` response — no error cases. Fix: enumerate its failure cases (`401 unauthorized`, `403 forbidden` if scoped, `404 not_found`) in the shared Problem-Details shape with each status + machine code + retryability, so a client can handle every outcome.

A bad finding is vague and unactionable:

> The error handling could be more complete. *(Which operation? Which errors? In what shape?)*

## Rules

**Hard rules (never violate):**

- **Emit exactly one verdict line, `VERDICT: approve` or `VERDICT: revise`** — that literal token, on its own line, nothing else on it. Downstream tooling parses it.
- **Judge, never author.** Return findings; do not rewrite, fix, or fill in the contract. The producer revises.
- **Single-sourced bar.** Judge against the twelve conditions in Step 2 — the same bar the author (`authoring-api-spec`'s Step-7 self-check) produces to. Do not invent extra conditions or apply a stricter private standard.
- **Aids are judged by outcome, never demanded.** The style notation (OpenAPI/SDL/proto), the named RFCs (9457/8594/9745/AIP), JSON-Schema fluency are the author's *techniques* — judge whether the operation is typed / the error catalog is complete / the examples match, NEVER "you didn't use OpenAPI / RFC 9457 / a `$ref`." (Error-model/type-both-sides/per-op-authorization OUTCOMES are real conditions cond-3/4/5 — only the techniques are aids.)
- **Style-agnostic — no OpenAPI reflex.** Never revise a GraphQL/gRPC contract for lacking HTTP status codes / OpenAPI / REST resources; judge its `errors`-array + nullability (GraphQL) or `google.rpc.Status` + proto (gRPC) instead. This is the cardinal drift this gate guards against.
- **No false-revise.** A contract that meets every applicable condition is approved, even a thin one for a small API. Revise only on a real, named gap. A thin API legitimately omits pagination, per-op scopes, a changelog.
- **No false-approve.** Never approve over a genuine gap to be agreeable. A happy-path-only operation, an untyped field, or a contradicting example is a `revise`.
- **The error model is not the happy path (cond. 5).** An operation showing only its `2xx` is a real gap (a client can't handle failures), not a style nit. The single most-skipped part of an api-spec.
- **Judge against the upstreams the document was given.** Assess the contract against its `depends_on` set + the docs it references. A **not-produced / not-handed-in** upstream (e.g. an absent feature-spec or data-model) is **never** a revise trigger. A contract that **ignored a produced upstream** it should have traced to **is** a fair finding.
- **Amend is delta-scoped.** When handed a change against an existing contract, review the delta + its classification + deprecation + ripple (cond-11) — do NOT full-re-review the unchanged contract, and do NOT demand a changelog on a greenfield first draft.
- **Greenfield consistency is N/A, not a gap.** When there is no shipped API to verify against (a new/proposed/fictional contract), mark cond-10's consistency check N/A — absence of a deployed surface to verify is never itself a blocker.
- **Every revise finding is actionable** — failed condition + location + concrete fix.

**Preferences (override-able):**

- Order findings by severity — blocking gaps first, then minor ones.
- Reference the condition number/name in each finding so the author maps it back to the bar.
- Keep approve-notes few and clearly non-blocking.

## Gotchas

- **Approving for completeness instead of callability.** Every section can be present and the API still un-callable (a happy-path-only operation, an untyped field, an example that contradicts its schema). Judge whether the *API can be called + implemented*, not whether the *template is filled*.
- **The OpenAPI reflex.** Demanding HTTP status codes of a GraphQL API, or OpenAPI of a gRPC API, is the dominant drift — a GraphQL contract is correct with the `errors` array + nullability, a gRPC one with `google.rpc.Status` + proto. Judge the style's own idiom.
- **The happy-path-only operation waved through.** An operation that lists its `200`/`201` and stops looks done — but with no error cases a client can't write the `catch` branch (cond. 5); enumerate every failure case or it is a gap.
- **The DTO-inversion / reverse-engineered contract.** A contract whose shapes contradict the upstream data-model, or whose operations were reverse-engineered from the published api-reference, inverts the dependency (cond. 6 / cond. 10) — the data-model is upstream, the api-reference downstream.
- **The example that drifts from the schema.** An example with a field the schema doesn't declare (or a wrong type/status) silently breaks the contract for whoever copies it (cond. 8).
- **Inventing conditions (the cardinal drift).** Adding a private requirement the bar does not carry ("you must use RFC 9457 / OpenAPI / a `$ref`") drifts the review-bar off the produce-bar. The techniques are judged by outcome only.
- **Systematic over-flagging (false-revise).** A reviewer asked to find problems tends to over-correct. A condition is a gap only on a *named, real* deficiency, not a decision you'd have made differently.
- **Confusing this with the api-reference or design-review.** An api-spec is judged for *whether the contract is callable + implementable* — distinct from the api-reference (the published consumer docs, a downstream consumer) and from `design-review` (which gates generic design docs/RFCs/ADRs/specs/plans). This gate is the doc-library api-spec artifact's dedicated reviewer.
- **Verdict token drift.** "Approved", "LGTM", "needs work", or a verdict buried mid-paragraph will not parse. Emit the literal `VERDICT: approve|revise` on its own line.

## Anti-patterns

- **Rubber-stamp approve.** Skimming and approving to avoid a revise loop — a happy-path-only operation or a DTO that contradicts the data-model waved through becomes an un-handleable failure or a wire/store mismatch.
- **Nit-pick revise.** Blocking on naming, notation, or nice-to-haves dressed up as gaps. Revise is for real callability/implementability blockers only.
- **OpenAPI-reflex revise.** Revising a GraphQL/gRPC contract for not using HTTP status codes / OpenAPI — the dominant api-spec-specific drift.
- **Silent rewrite.** "It was easier to just fix the contract" — authoring inside a review collapses the produce/judge separation.
- **Inventing conditions.** Adding a requirement the bar does not carry (a named notation/RFC) — judged by outcome only.
- **Full-re-reviewing an amend.** Re-judging the whole unchanged contract on a small delta — review the delta + its classification + deprecation + ripple (cond. 11), proportionally.
- **Hedged verdict.** "Mostly approve but…" or two verdict lines. Exactly one decision, exactly one token.

## Output

A single review result for one api-spec doc:

- **One verdict line** — `VERDICT: approve` or `VERDICT: revise`, verbatim, on its own line.
- **Findings** — on `revise`, one actionable finding per blocking gap (failed condition + location + concrete fix); on `approve`, optional non-blocking notes.

The abstract consumer is whatever orchestrates the produce→review loop: `approve` accepts the contract for integration/implementation; `revise` returns the findings to the producer for a bounded revision pass. **Medium:** the artifact judged is a **textual-markdown** api-spec today (operation tables + fenced schema blocks + example pairs); the bar is medium-independent.

## Related

- **`authoring-api-spec`** — the produce half of the pair; it writes the contract to the same eleven-condition bar this skill judges against (its Step-7 self-check). Pairing them single-sources the bar so produce and review do not drift.
- A **data-model** (where it exists) — *upstream*; the wire DTOs reference its entities (one-directional); cond-6/cond-10 check the contract references it, not redefines/contradicts it.
- The upstream **feature-spec** — the behaviors the contract exposes; cond-2/cond-10 trace to it (judged only when handed in).
- **`reviewing-api-reference`** — the gate for the *downstream* published api-reference (often generated from this contract). This contract is that reference's source of truth (cond-10's one-directional rule); never reverse-engineered from it.
- A **`design-review`** skill — the gate for *generic* engineering design docs, RFCs, ADRs, specs, and plans (it verifies claims against the codebase). This skill is the dedicated reviewer for the doc-library **api-spec** artifact; `design-review` carves that artifact out.
- An **api-spec template / content-template** tool — owns the section *structure*; this skill judges *quality against the bar*, not structural conformance.

## Progressive disclosure

- `references/api-spec-quality-bar.md` — the twelve checklist conditions expanded with per-condition pass/gap signals and worked finding examples (the typed-both-sides check, the complete-error-model check, the shared-types/reference-data-model check, the per-operation-authorization check, the pagination/tie-breaker check, the examples-match-schemas check, the one-directional/consistency-with-shipped-API check, the style-agnostic guard, and the delta-scoped-amend signals). Load when a borderline condition needs a sharper pass/gap call.
- `references/sources.md` — research provenance for the review method (OpenAPI/JSON-Schema, GraphQL SDL, gRPC/proto, RFC 9110/9457, RFC 8594/9745, AIP-180/185, pagination + rate-limit conventions).

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap); combined `description` + `when_to_use` truncated at 1,536 chars in the listing.
- Body ~500 lines / 5,000 tokens (soft target — quality takes precedence; flag if consistently over 700 lines / 7,000 tokens) — kept in context every turn.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k tokens, error >50k.

## Changelog

- **1.0.0** (2026-06-15) — initial release. Net-new reviewer forged by adapting the canonical sibling `reviewing-data-model`; the eleven-condition contract-completeness bar single-sourced 1:1 with `authoring-api-spec`'s Step-7 self-check; style-agnostic (no OpenAPI reflex); inherits the `VERDICT: approve|revise` contract, judge-against-given-upstreams, the consistency-with-shipped-API verify-against-code discipline + greenfield clause, and the proportionality / no-false-revise / inventing-conditions anti-patterns.
