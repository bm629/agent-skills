---
name: reviewing-api-reference
description: >
  Use when reviewing/judging a published, consumer-facing API reference an
  integrating client developer calls an API from — deciding if a developer can
  integrate from it. A gate, not authoring. Judges it against a single-sourced
  usability + contract-consistency bar: getting-started + auth reach a first call;
  every api-spec operation is documented with purpose + typed params + a worked
  example + its errors; the reference is CONSISTENT WITH THE HANDED-IN api-spec
  (every endpoint/param/shape/error traces to the contract — no drift, no fabricated
  endpoints — the load-bearing check); errors + rate-limits documented; samples
  runnable; versioning stated; gaps surfaced. Emits exactly `VERDICT: approve|revise`
  plus actionable findings; approves a reference meeting the bar (no false-revise of
  a proportionally-sized one), revises on a named gap. Not for authoring it, not the
  end-user user-guide (user-guide-review), not the developer adoption guide
  (developer-guide-review), not the engineering api-spec (design-review).
extensions:
  claude:
    when_to_use: "judging a finished, published API reference against the usability + contract-consistency bar (consistency with the handed-in api-spec being load-bearing) and emitting an approve/revise verdict"
    argument-hint: "<the finished API reference to review, plus the handed-in api-spec to check consistency against>"
version: "1.0.0"
forge:
  status: reviewed
  forged: 2026-06-05
  reviewed: 2026-06-05
---

# `reviewing-api-reference` — SKILL.md

> **Variant:** standard · **When to use:** judging a finished, published API reference as an acceptance gate — checking a client developer can integrate from it and that it stays consistent with the handed-in api-spec contract, then emitting `VERDICT: approve|revise` with actionable findings.

## Overview

This skill is the *review* half of an authoring/judging api-reference pair. Loaded by a reviewer who holds a **finished, published API reference** — the consumer-facing documentation an integrating client developer reads to call an API (getting-started, authentication, a per-endpoint reference, shared object types, errors + rate-limits, code samples, a changelog) — it judges that document against one question: **can a client developer authenticate, make a first call, and integrate every operation from this reference alone, and does every documented endpoint, shape, and error trace to the upstream api-spec contract — no drift, nothing fabricated?** It applies a fixed **usability + contract-consistency checklist** — the same bar an api-reference author produces to, so the produce-bar and the review-bar do not drift — then emits a single machine-parseable verdict plus findings the author can act on in one revision pass. It is an acceptance gate: it does **not** author, fix, or rewrite the reference; it judges and returns findings, and the producer revises.

The **single most load-bearing check** is **api-spec-consistency**: the reference is downstream of the engineering **api-spec** wire contract, and the reviewer **spot-checks the documented endpoints, parameters, shapes, and errors against the handed-in api-spec**. Drift or a fabricated/orphan endpoint is the highest-impact defect class.

## When to activate

- A finished, published API reference needs an accept/revise decision before it ships to integrating developers.
- You are the independent reviewer / gate for an API reference a producer just authored, and you have the upstream api-spec to check consistency against.
- Re-judging a revised API reference after a prior `revise` verdict.

**Do NOT activate when:**

- Authoring or repairing an API reference -> use an api-reference-authoring skill (it produces to the same bar this skill asserts). This skill never writes the document.
- Reviewing the **end-user product guide** — the task help a non-technical person using the product reads -> use a user-guide-review skill. Different audience, different bar; this judges the developer integration reference.
- Reviewing the **developer adoption / integration guide** — an SDK / CLI / platform how-to + concepts narrative that *points into* this reference -> use a developer-guide-review skill. That gate judges the adoption narrative; **this** gate judges the endpoint catalog / reference it links to.
- Reviewing the **engineering api-spec** — the wire contract itself (operations, exhaustive schemas, the internal error model) -> use a design-review skill that verifies design claims against the codebase. That gates the *contract*; **this** judges the *published consumer reference derived from* that contract. Distinct artifact, distinct audience, distinct bar.
- Checking template/section conformance -> that is a template concern. This skill judges *quality against the bar*, not whether every heading is present.
- Grading a project's live API implementation -> this gate judges the *reference document*, not the running service.

## Workflow

### Step 1: Read the whole reference with fresh, independent eyes — and pull up the api-spec

Read the API reference end to end as if you were an integrating developer encountering the API for the first time, without the author's framing. Your stance is a gatekeeper for the integrating developer: a finding carries weight only when it shows a developer **cannot authenticate, make a first call, or integrate an operation as written**, or when the reference **diverges from the contract**. Identify the **API archetype** the reference is sized to (a thin few-endpoint utility vs. a broad multi-resource platform) — Step 2's proportionality calibration depends on it. Critically, **load the handed-in upstream api-spec**: it is your **endpoint-coverage checklist and your consistency oracle**. If the api-spec was **not handed in**, record that now — you will flag it as an assumption in Step 4 and judge usability on what you have, since the consistency dimension cannot be fully run without the contract.

### Step 2: Run the usability + contract-consistency checklist — judge each condition

For each condition below, decide **pass** or **gap**. A condition fails only on a *real, named* deficiency — "I'd have organized the endpoints differently" is not a gap. For each gap, capture the exact location and what is missing (Step 4 turns it into an actionable finding). These conditions are the **single-sourced bar** (the shared api-reference dossier — the same conditions an api-reference author produces to); do not add private ones.

1. **First call is reachable.** Getting-started + authentication together let a developer **authenticate and make a first successful call** end to end, copy-paste, **before** any advanced feature. *Gap* when getting-started or auth is missing, or the onboarding path doesn't reach one working call without the developer guessing.
2. **Every operation documented.** Every operation in the **handed-in api-spec** appears in the reference with **all of**: purpose, typed parameters (required/optional + constraints), a **worked request example**, a **worked response example**, and its **error responses**. *Gap* when a contract operation is missing from the reference, or a documented operation shows only the `200` body with no params / no worked example / no errors.
3. **Errors are first-class.** One consistent error-response shape is documented once; a status-code table gives cause + remedy; per-endpoint error rows name the failures each endpoint returns. *Gap* when the reference covers only the 2xx happy path, or documents errors only generically with no per-endpoint rows.
4. **Rate limits documented.** The limit, the `429` signal, the `Retry-After` header (and `RateLimit-*` / `X-RateLimit-*` where present), backoff, and idempotency keys for safe retries. *Gap* when an API that rate-limits leaves this undocumented (a thin API that doesn't rate-limit legitimately omits it — see Proportionality).
5. **Consistent with the handed-in api-spec — no drift, nothing fabricated.** Every endpoint, field type, required/optional flag, error code, and auth scheme in the reference **traces to the upstream api-spec**. The reference adds narrative + onboarding + worked examples; it does **not** redefine, contradict, or invent against the contract. *Gap* when a documented endpoint is **not declared by the contract** (a fabricated/orphan endpoint), when a field/type/required-flag/error code/auth scheme **contradicts** the contract, or when an operation the contract declares is **absent** from the reference. **Spot-check the documented endpoints, parameters, shapes, and errors against the handed-in api-spec** — this is the **load-bearing** dimension; the highest-impact defect is the reference diverging from the contract.
6. **Samples are runnable.** curl + at least one language, with realistic values that **match the schemas exactly** — an example contradicting its schema (a field the contract doesn't declare, a wrong type or status) is a defect. More languages **only** where an official SDK exists. *Gap* when there are no runnable samples, or a sample contradicts the contract's shapes.
7. **Versioning stated.** How versions are expressed, how a developer pins/upgrades, what counts as a breaking change, the deprecation policy, and a dated changelog. *Gap* when versioning is silent for an API that versions.
8. **Define shapes once.** Shared object / data types live in **one** core-objects section and are **referenced** by the per-endpoint blocks, not redefined per endpoint. *Gap* when a reusable resource is redefined inside every endpoint (a drift hazard) instead of referenced.
9. **Grounded, gaps surfaced.** Endpoints reflect the api-spec; conventions reflect established practice; genuine gaps (a missing usage context, an undocumented limit) are surfaced as **explicit assumptions/open-questions**, not invented to look complete. *Gap* when content was **fabricated** to look finished instead of flagged.

**Proportionality.** "Can a developer integrate from it" scales with the API. A thin API's reference legitimately **collapses sections it does not need** — pagination disappears if nothing lists, the SDK/language table waits until SDKs exist, the changelog starts with one row, rate-limits are absent if the API doesn't limit. That is correct sizing, not a gap. Judge the **developer's ability to integrate**, not word count or section count. A small, complete reference that satisfies every *applicable* condition **passes**. Do not manufacture a gap from brevity. (Conditions 2 and 5 still bind at any size: every contract operation present, everything traced to the contract.)

### Step 3: Decide the verdict

- **approve** — every applicable condition passes. A client developer can authenticate, make a first call, and integrate every operation from this reference as written, and everything traces to the api-spec. Approve even if you can imagine stylistic improvements; the bar is usability + contract-consistency, not perfection — and not maximalism.
- **revise** — one or more conditions have a real, named gap that blocks integration (a missing or undocumented operation, drift or a fabricated endpoint vs the contract, missing getting-started or auth, happy-path-only endpoints, a sample that contradicts the schema, fabricated content, etc.).

Do not revise to signal effort or to request nice-to-haves. A condition is either met or it isn't.

### Step 4: Emit the verdict + actionable findings

Emit the verdict as a single line — the literal text `VERDICT: approve` or `VERDICT: revise`, on its own line, with **no** surrounding code fences, quotes, or extra words (the fences here are illustration only):

```
VERDICT: approve
```

Then, on the following lines, list findings. On `revise`, every finding is **actionable** — the failed condition, the exact location, and **how to fix it** — so the author can resolve it in one pass. On `approve`, findings are optional non-blocking notes; do not let them imply a revision is required.

If the **api-spec was not handed in**, state that as an explicit assumption in the findings (e.g. "api-spec not provided — consistency (cond. 5) judged only against the reference's internal coherence; provide the contract for a full trace") and judge the other conditions on what you have. Do not silently pass over the un-runnable consistency check.

A good finding names the gap and the fix:

> **revise** — api-spec-consistency (cond. 5), "POST /v1/refunds": the reference documents this endpoint, but the handed-in api-spec declares no `refunds` operation. Fix: remove the orphan endpoint, or — if the contract is meant to carry it — flag it back to the api-spec author; the reference must not invent an endpoint the contract doesn't declare.

> **revise** — Every operation documented (cond. 2), "GET /v1/widgets/{id}": shows a `200` response body but no parameters, no worked request example, and no error responses. Fix: add the typed path param (`id`, string, required), a worked curl request, and the error rows the contract lists for it (e.g. `404 not_found`).

A bad finding is vague and unactionable:

> The error documentation could be more thorough. *(Which endpoint? Which errors? What fixes it?)*

## Rules

**Hard rules (never violate):**

- **Emit exactly one verdict line, `VERDICT: approve` or `VERDICT: revise`** — that literal token, on its own line, nothing else on it. Downstream tooling parses it (a verdict-parsing contract). No alternate verdict vocabulary.
- **Judge, never author.** Return findings; do not rewrite, fix, or fill in the reference. The producer revises.
- **Single-sourced bar.** Judge against the nine conditions in Step 2 — the same bar the author produces to (the shared api-reference dossier). Do not invent extra conditions or apply a stricter private standard.
- **api-spec-consistency is the load-bearing dimension.** Spot-check the documented endpoints, parameters, shapes, and errors against the **handed-in api-spec**. A fabricated/orphan endpoint, a field the contract doesn't declare, a type/required-flag/error/auth that contradicts the contract, or a contract operation absent from the reference is the highest-impact defect (cond. 5).
- **No false-revise.** A reference that meets every applicable condition is approved, even a thin one for a small API. Proportional sizing that still covers the contract is not a defect. Revise only on a real, named gap.
- **No false-approve.** Never approve over a genuine gap to be agreeable. A blocking gap is a `revise`.
- **Happy-path-only is a gap.** An endpoint that shows only the `2xx` body with no parameters, no worked example, or no error responses fails condition 2.
- **A sample that contradicts the schema is a gap.** A worked example or code sample using a field the contract doesn't declare, or a wrong type/status, fails condition 6.
- **Fabrication is a gap, not grounding.** An invented endpoint, parameter, status code, or limit presented as fact fails condition 9 — a real gap should be flagged as an assumption/open-question, not papered over.
- **Missing api-spec is flagged, not silently passed.** If the contract wasn't handed in, surface it as an explicit assumption and note that consistency (cond. 5) could not be fully run; judge the rest on what you have.
- **Judge against the upstreams the document was given.** Assess the reference against its `depends_on` set (the upstream documents the project actually produced — primarily the api-spec). A **not-produced** upstream is **never** a revise trigger — never invent an expectation of a document the project didn't make. But a reference that **ignored a produced upstream** it should have drawn on (e.g. the handed-in api-spec whose operations the reference doesn't reflect) **is** a fair finding.
- **Every revise finding is actionable** — failed condition + location + concrete fix. No vague notes.

**Preferences (override-able):**

- Order findings by severity — blocking gaps first (api-spec-consistency drift / fabrication first of all), then minor ones.
- Reference the condition number/name in each finding so the author maps it back to the bar.
- Keep approve-notes few and clearly non-blocking.

## Gotchas

- **Approving for completeness instead of integrability.** Every section can be present and the API still un-integrable (no reachable first call, endpoints showing only the `200` body, samples that contradict the schema). Judge whether a developer can *integrate from it*, not whether the *template is filled*.
- **The drift that reads consistent.** The reference and the api-spec can both look right in isolation while disagreeing — a field the reference shows that the contract never declared, an endpoint the contract dropped, an error the reference omits. The only way to catch it is to **trace documented endpoints/shapes/errors against the handed-in api-spec** (cond. 5). This is the single most damaging and most easily-missed defect.
- **The fabricated/orphan endpoint.** A reference can document an endpoint that looks plausible but the contract never declares — an invented operation that no server implements. Spot-check the endpoint index against the api-spec one-to-one; an endpoint with no contract backing is a defect, not coverage.
- **Happy-path-only endpoints.** An endpoint block that shows the `200` body and stops reads complete but leaves the developer to discover failure modes by trial and error. Each operation needs its parameters, at least one worked example, and its error responses (cond. 2/3).
- **The sample that drifts from the schema.** A curl or code sample using a field the contract doesn't carry (or a wrong type/status) breaks silently — it looks like a worked example but won't run against the real API. Check samples against the contract's shapes (cond. 6).
- **Re-typed generated catalogs.** Where the endpoint catalog is generated from OpenAPI, a *hand-retyped* duplicate of it drifts immediately. If you see a manually-maintained copy of a generated catalog, that is a drift hazard worth a finding; the generated catalog itself staying current is fine.
- **Missing-contract blind spot.** If the api-spec wasn't handed in, the consistency dimension can't be fully run — do not let that absence default to an approve. Flag it as an assumption (cond. 5 partially un-runnable) and judge the rest.
- **Systematic over-flagging (false-revise).** A reviewer asked to find problems — especially one also asked to propose fixes — tends to over-correct, judging sound references as defective. Calibrate to the bar: a condition is a gap only on a *named, real* deficiency, not on an organization or example you'd have written differently. Plausible-sounding nits are the dominant reviewer error here.
- **False-revise on a proportionally-sized reference.** A thin API's reference is correctly small — a handful of endpoints, no pagination if nothing lists, a one-row changelog, no SDK table until SDKs exist. That is right-sizing, not under-documentation. Manufacturing a gap from brevity drives avoidable revise loops; calibrate to the archetype (conditions 2 and 5 still bind: every contract operation present and traced).
- **Confusing this with the user-guide, developer-guide, or design-review gate.** This judges the **published developer reference / endpoint catalog**. A user-guide-review judges the end-user product help; a developer-guide-review judges the SDK/CLI adoption narrative that *points into* this reference; design-review gates the engineering *api-spec contract*. Don't apply an end-user, an adoption-narrative, or a wire-contract bar to the consumer reference.
- **Verdict token drift.** "Approved", "LGTM", "needs work", or a verdict buried mid-paragraph will not parse. Emit the literal `VERDICT: approve|revise` on its own line.

## Anti-patterns

- **Rubber-stamp approve.** Skimming and approving to avoid a revise loop — the gate exists to catch references no developer can integrate from; a fabricated endpoint, a drift from the contract, or a happy-path-only block waved through becomes a broken integration or a mid-build support ticket.
- **Skipping the api-spec trace.** "The reference looks internally consistent, so I'll approve" — without spot-checking against the handed-in contract you miss the highest-impact defect class (cond. 5). Reviewing the reference in isolation is the one shortcut this gate exists to forbid.
- **Nit-pick revise.** Blocking on endpoint-ordering taste, wording preference, or nice-to-haves dressed up as gaps. Revise is for real usability/consistency blockers only.
- **Silent rewrite.** "It was easier to just fix the example" — authoring inside a review collapses the produce/judge separation and removes the author's chance to learn the gap.
- **Inventing conditions.** Adding a private requirement the bar does not carry ("it should also include a Postman collection / a GraphQL variant") drifts the review-bar off the produce-bar and causes spurious revises. Judge the nine conditions only.
- **Maximalism.** Demanding pagination, a multi-language SDK matrix, or a long changelog from a thin API that doesn't need them. The bar is the developer's ability to integrate, not the largest possible reference.
- **Hedged verdict.** "Mostly approve but…" or two verdict lines. Exactly one decision, exactly one token.

## Output

A single review result for one published API reference:

- **One verdict line** — `VERDICT: approve` or `VERDICT: revise`, verbatim, on its own line.
- **Findings** — on `revise`, one actionable finding per blocking gap (failed condition + location + concrete fix); on `approve`, optional non-blocking notes.

The reference under review is **textual** today — endpoint sections + fenced request/response examples + fenced code samples (markdown via the local docs backend); the review **method + bar are medium-independent** (a future rendered docs site changes only the medium, not what is judged). The **abstract consumer** is whatever orchestrates the produce->review loop: `approve` accepts the API reference for use by integrating developers; `revise` returns the findings to the producer for a bounded revision pass.

## Related

- An **api-reference-authoring** skill (`authoring-api-reference`) — the produce half of the pair; it writes the reference to the same usability + contract-consistency bar this skill judges against, and **owns the shared dossier** this skill reuses. Pairing them single-sources the bar so produce and review do not drift.
- The upstream **api-spec** (`authoring-api-spec`) — the engineering wire contract every endpoint, field, and error in the reference derives from; this gate **checks the reference for consistency against the handed-in api-spec** (cond. 5). The api-spec itself is gated at engineering time by a design-review skill, not here.
- A **user-guide-review** skill — the gate for the end-user product guide (the non-technical person using the product). Distinct doc, distinct audience/bar; not the developer reference.
- A **developer-guide-review** skill — the gate for the SDK/CLI/platform adoption + integration narrative that *points into* this reference. Distinct doc, distinct bar; this judges the endpoint catalog it links to.
- A **design-review** skill — the gate for engineering design documents, including the **engineering api-spec** wire contract, which verifies claims against the codebase. Distinct gate, distinct artifact; not for the published consumer reference.
- An **api-reference template / content-template** tool — owns the section *structure*; this skill judges *quality against the bar*, not structural conformance.

## Progressive disclosure

- `references/sources.md` — research provenance for the review method (the single-sourced usability + contract-consistency quality bar from the shared api-reference dossier, the per-endpoint anatomy + errors + rate-limit conventions, the drift / generation-adaptive evidence, and the reviewer-overcorrection basis for the no-false-revise discipline). Load only to audit where the guidance came from.

## Body budget

- `description` <= 1,024 chars (agentskills.io cap). Claude truncates the combined `description` + `when_to_use` at 1,536 chars in the listing.
- Body <= ~500 lines / 5,000 tokens — kept in context every turn.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k tokens, error >50k.
