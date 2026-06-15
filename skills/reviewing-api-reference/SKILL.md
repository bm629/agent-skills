---
name: reviewing-api-reference
description: >
  Use when reviewing/judging a published, consumer-facing API reference an
  integrating developer calls an API from — deciding if they can integrate from
  it. A gate, not authoring. Judges against a single-sourced 11-condition
  usability + contract-consistency bar: getting-started + auth reach a first
  call; every api-spec operation (incl. events/webhooks) is documented with
  purpose + typed params + a worked example + errors; errors first-class;
  rate-limits + pagination documented where applicable; versioning +
  deprecation/sunset stated; the reference is CONSISTENT WITH THE HANDED-IN
  api-spec (no drift, no fabricated endpoint — the load-bearing check); samples
  runnable; an amendment re-syncs to the changed contract. Emits exactly
  `VERDICT: approve|revise` plus actionable findings; approves a
  proportionally-sized reference, revises on a named gap. Not authoring it,
  not the end-user user-guide, not the developer-adoption guide, not the
  engineering api-spec (reviewing-api-spec).
extensions:
  claude:
    when_to_use: "judging a finished or amended API reference against the 11-condition usability + contract-consistency bar (consistency with the handed-in api-spec being load-bearing) and emitting an approve/revise verdict"
    argument-hint: "<the finished/amended API reference to review, plus the handed-in api-spec to check consistency against (and the change request, on an amendment)>"
version: "1.1.0"
forge:
  status: reviewed
  forged: 2026-06-05
  reviewed: 2026-06-14
---

# `reviewing-api-reference` — SKILL.md

> **Variant:** standard · **When to use:** judging a finished (or amended) published API reference as an acceptance gate — checking a client developer can integrate from it and that it stays consistent with the handed-in api-spec contract, then emitting `VERDICT: approve|revise` with actionable findings.

## Overview

This skill is the *review* half of an authoring/judging api-reference pair. Loaded by a reviewer who holds a **finished, published API reference** — the consumer-facing documentation an integrating client developer reads to call an API (getting-started, authentication, a per-endpoint reference, events/webhooks, shared object types, pagination, errors + rate-limits, code samples, an API changelog) — it judges that document against one question: **can a client developer authenticate, make a first call, and integrate every operation from this reference alone, and does every documented endpoint, shape, and error trace to the upstream api-spec contract — no drift, nothing fabricated?** It applies a fixed **11-condition usability + contract-consistency checklist** — the same bar an api-reference author produces to, so the produce-bar and the review-bar do not drift — then emits a single machine-parseable verdict plus findings the author can act on in one revision pass. It is an acceptance gate: it does **not** author, fix, or rewrite the reference; it judges and returns findings, and the producer revises.

The **single most load-bearing check** is **api-spec-consistency** (cond. 5): the reference is downstream of the engineering **api-spec** wire contract, and the reviewer **spot-checks the documented endpoints, parameters, shapes, and errors against the handed-in api-spec**. Drift or a fabricated/orphan endpoint is the highest-impact defect class.

## When to activate

- A finished, published API reference needs an accept/revise decision before it ships to integrating developers.
- You are the independent reviewer / gate for an API reference a producer just authored, and you have the upstream api-spec to check consistency against.
- Re-judging a revised API reference after a prior `revise` verdict.
- Judging an **amendment** of an existing reference (a delta after the upstream contract changed) — the delta-scoped path (cond. 11).

**Do NOT activate when:**

- Authoring or repairing an API reference -> use an api-reference-authoring skill (it produces to the same bar this skill asserts). This skill never writes the document.
- Reviewing the **end-user product guide** — task help a non-technical person using the product reads -> use a user-guide-review skill. Different audience, different bar.
- Reviewing the **developer adoption / integration guide** — an SDK/CLI/platform how-to + concepts narrative that *points into* this reference -> use a developer-guide-review skill. That judges the adoption narrative; **this** judges the endpoint catalog / reference it links to.
- Reviewing the **engineering api-spec** — the wire contract itself (operations, exhaustive schemas, the internal error model) -> use `reviewing-api-spec`, its dedicated gate (the generic `design-review` carves the api-spec artifact out to it). That gates the *contract*; **this** judges the *published consumer reference derived from* that contract.
- Checking template/section conformance -> that is a template concern. This skill judges *quality against the bar*, not whether every heading is present.
- Grading a project's live API implementation -> this gate judges the *reference document*, not the running service.

## Workflow

### Step 1: Read the whole reference with fresh, independent eyes — and pull up the api-spec

Read the API reference end to end as if you were an integrating developer encountering the API for the first time, without the author's framing. Your stance is a gatekeeper for the integrating developer: a finding carries weight only when it shows a developer **cannot authenticate, make a first call, or integrate an operation as written**, or when the reference **diverges from the contract**. Identify the **API archetype** the reference is sized to (a thin few-endpoint API-key utility vs. a broad multi-resource platform vs. an event-driven/webhook API) — Step 2's proportionality calibration depends on it. Critically, **load the handed-in upstream api-spec**: it is your **endpoint-coverage checklist and your consistency oracle**. If the api-spec was **not handed in**, record that now — you will flag it as an assumption in Step 4 and judge usability on what you have, since the consistency dimension cannot be fully run without the contract. **On an amendment**, also note the change request / changed-contract delta — it switches on the delta-scoped path (cond. 11).

### Step 2: Run the usability + contract-consistency checklist — judge each condition

For each condition below, decide **pass** or **gap**. A condition fails only on a *real, named* deficiency — "I'd have organized the endpoints differently" is not a gap. For each gap, capture the exact location and what is missing (Step 4 turns it into an actionable finding). These conditions are the **single-sourced bar** (the same conditions an api-reference author produces to); do not add private ones.

1. **First call is reachable.** Getting-started + authentication together let a developer **authenticate and make a first successful call** end to end, copy-paste, **before** any advanced feature. The auth section names the scheme/flow (API key / which OAuth2 flow), where to get + how to send credentials, and shows the **auth-failure** (`401`/`403`) case, not just success. *Gap* when getting-started or auth is missing, the scheme/flow is unnamed, the failure case is absent, or the onboarding path doesn't reach one working call without guessing.
2. **Every operation documented.** Every operation in the **handed-in api-spec** — **including contract-declared events/webhooks** (an event is an "operation" for this condition) — appears with **all of**: purpose, typed parameters (required/optional + constraints), a **worked request example**, a **worked response example**, and its **error responses**. *Gap* when a contract operation/event is missing, or a documented one shows only the `200` body with no params / no worked example / no errors.
3. **Errors are first-class.** One consistent error-response shape documented once (a **Problem-Details-shaped** body — RFC 9457 `application/problem+json`, or the API's own consistent shape) with a **machine-readable `code`** distinct from the HTTP status; a status-code table (cause + remedy) using **semantically-correct** statuses (429 rate-limit, 409 conflict, 410 sunset — not a generic 400); per-endpoint error rows. *Gap* when the reference covers only the 2xx happy path, documents errors only generically with no per-endpoint rows, or uses the wrong status class.
4. **Rate limits documented.** The limit, the `429` signal, `Retry-After`, the `RateLimit-*` / `X-RateLimit-*` headers where present (noting they're replaced by `Retry-After` on a 429), backoff **+ jitter**, and **idempotency keys** for safe retried writes. *Gap* when an API that rate-limits / accepts writes leaves this undocumented (a thin API that doesn't rate-limit legitimately omits it — see Proportionality).
5. **Consistent with the handed-in api-spec — no drift, nothing fabricated.** Every endpoint, field type, required/optional flag, error code, event, and auth scheme in the reference **traces to the upstream api-spec**. The reference adds narrative + onboarding + worked examples; it does **not** redefine, contradict, or invent against the contract. *Gap* when a documented endpoint/event is **not declared by the contract** (a fabricated/orphan one), when a field/type/required-flag/error/auth **contradicts** the contract, when an operation the contract declares is **absent**, or when the reference is a **hand-retyped duplicate of a generated catalog** (a drift hazard). **Spot-check the documented endpoints, parameters, shapes, and errors against the handed-in api-spec** — the **load-bearing** dimension; the highest-impact defect is the reference diverging from the contract.
6. **Samples are runnable.** curl + at least one language, with realistic values that **match the schemas exactly** — an example contradicting its schema (a field the contract doesn't declare, a wrong type or status) is a defect. More languages **only** where an official SDK exists. *Gap* when there are no runnable samples, or a sample contradicts the contract's shapes.
7. **Versioning + deprecation stated.** How versions are expressed, how a developer pins/upgrades, what counts as a breaking change, a dated changelog — **and**, for any deprecated surface, the deprecation/sunset mechanics (Deprecation/Sunset, `410 Gone` after sunset) + a **migration path/guide**. *Gap* when versioning is silent for an API that versions, or a deprecated endpoint carries no migration path (a v1-only API with nothing deprecated legitimately has a thin section).
8. **Define shapes once.** Shared object / data types live in **one** core-objects section and are **referenced** by the per-endpoint/event blocks, not redefined per endpoint. *Gap* when a reusable resource is redefined inside every endpoint (a drift hazard) instead of referenced.
9. **Grounded, gaps surfaced.** Endpoints/events reflect the api-spec; conventions reflect established practice; genuine gaps (a missing usage context, an undocumented limit) are surfaced as **explicit assumptions/open-questions**, not invented to look complete. *Gap* when content was **fabricated** to look finished instead of flagged.
10. **Pagination / list-operation conventions** (proportional). For an API with **list operations**, the reference documents — once, at the reference level — the pagination model (cursor/offset), standard parameter names, response metadata (`has_more`/`next_cursor`), a default + a documented **max** page size, the last-page signal, and a **stable, tie-broken sort** (a unique secondary key so ordering is deterministic across pages). *Gap* when list endpoints leave the model / max page size / tie-broken sort undocumented. **n/a for an API with no list operations** — do not manufacture a gap.
11. **Amend — delta re-syncs to the changed contract** (only on an amendment). Handed a change request / changed-contract delta: the changed blocks meet the bar; the delta **re-syncs to the (now-changed) api-spec** (cond. 5 on the delta); **samples re-synced** (cond. 6 — no stale sample after a schema change); deprecation/migration documented where an endpoint changed/was removed (cond. 7); the **doc's own version + amend-log** updated (distinct from the API changelog). It is a **delta-scoped** review — NOT a full re-review of the unchanged catalog. **n/a on a greenfield first build** (no change request handed in — detected by the input signal).

**Proportionality.** "Can a developer integrate from it" scales with the API. A thin API's reference legitimately **collapses sections it does not need** — pagination disappears if nothing lists (cond. 10 n/a), the SDK/language table waits until SDKs exist, the changelog starts with one row, rate-limits are absent if the API doesn't limit, webhooks/deprecation are absent until they apply, cond. 11 is n/a on a first build. That is correct sizing, not a gap. Judge the **developer's ability to integrate**, not word count or section count. A small, complete reference that satisfies every *applicable* condition **passes**. (Conditions 2 and 5 still bind at any size: every contract operation/event present, everything traced to the contract.)

### Step 3: Decide the verdict

- **approve** — every applicable condition passes. A client developer can authenticate, make a first call, and integrate every operation from this reference as written, and everything traces to the api-spec. Approve even if you can imagine stylistic improvements; the bar is usability + contract-consistency, not perfection — and not maximalism.
- **revise** — one or more conditions have a real, named gap that blocks integration (a missing/undocumented operation or event, drift or a fabricated endpoint vs the contract, missing getting-started/auth or the auth-failure case, happy-path-only endpoints, a sample that contradicts the schema, undocumented list-pagination on a listing API, a deprecated endpoint with no migration path, a botched amendment with stale samples, fabricated content, etc.).

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

> **revise** — Pagination conventions (cond. 10), "GET /v1/widgets": the list endpoint documents `limit` but no maximum page size and no stable-sort tie-breaker, so ordering is non-deterministic across pages. Fix: document the max page size and the secondary sort key (e.g. ordered by `created` then `id`).

> **revise** — Amend (cond. 11), "Charge object": the api-spec added `currency` and the field is documented, but the worked response example and the Python sample still omit it. Fix: re-sync the Charge examples + samples to include `currency` (cond. 6).

A bad finding is vague and unactionable:

> The error documentation could be more thorough. *(Which endpoint? Which errors? What fixes it?)*

## Rules

**Hard rules (never violate):**

- **Emit exactly one verdict line, `VERDICT: approve` or `VERDICT: revise`** — that literal token, on its own line, nothing else on it. Downstream tooling parses it. No alternate verdict vocabulary.
- **Judge, never author.** Return findings; do not rewrite, fix, or fill in the reference. The producer revises.
- **Single-sourced bar.** Judge against the eleven conditions in Step 2 — the same bar the author produces to. Do not invent extra conditions or apply a stricter private standard.
- **api-spec-consistency is the load-bearing dimension.** Spot-check the documented endpoints, parameters, shapes, events, and errors against the **handed-in api-spec**. A fabricated/orphan endpoint, a field/type/required-flag/error/auth that contradicts the contract, a contract operation/event absent from the reference, or a hand-retyped duplicate of a generated catalog is the highest-impact defect (cond. 5).
- **No false-revise.** A reference that meets every applicable condition is approved, even a thin one for a small API. Proportional sizing that still covers the contract is not a defect. Revise only on a real, named gap. **API-style overlays + webhook-documentation technique are AIDS judged by outcome** (a webhook reference is judged via cond. 2/3/5, never "add a webhook/GraphQL section"); the rendered-docs-site features (search, an interactive try-it / Postman, a11y/i18n) are **out of scope** — never a revise trigger for a markdown reference.
- **No false-approve.** Never approve over a genuine gap to be agreeable. A blocking gap is a `revise`.
- **Happy-path-only is a gap.** An endpoint that shows only the `2xx` body with no parameters, no worked example, or no error responses fails condition 2.
- **A sample that contradicts the schema is a gap.** A worked example or code sample using a field the contract doesn't declare, or a wrong type/status, fails condition 6 — including a stale sample left unchanged after an amendment.
- **Fabrication is a gap, not grounding.** An invented endpoint, parameter, status code, event, or limit presented as fact fails condition 9 — a real gap should be flagged as an assumption/open-question.
- **Missing api-spec is flagged, not silently passed.** If the contract wasn't handed in, surface it as an explicit assumption and note that consistency (cond. 5) could not be fully run; judge the rest on what you have.
- **Amend is delta-scoped (cond. 11).** On an amendment, review the delta — re-synced to the changed contract, samples re-synced, deprecation/migration documented, the doc version + amend-log updated — NOT a full re-review of the unchanged catalog. n/a on a greenfield first build.
- **Judge against the upstreams the document was given.** Assess the reference against its `depends_on` set (primarily the api-spec). A **not-produced** upstream is **never** a revise trigger. But a reference that **ignored a produced upstream** (e.g. the handed-in api-spec whose operations the reference doesn't reflect) **is** a fair finding.
- **Every revise finding is actionable** — failed condition + location + concrete fix. No vague notes.

**Preferences (override-able):**

- Order findings by severity — blocking gaps first (api-spec-consistency drift / fabrication first of all), then minor ones.
- Reference the condition number/name in each finding so the author maps it back to the bar.
- Keep approve-notes few and clearly non-blocking.

## Gotchas

- **Approving for completeness instead of integrability.** Every section can be present and the API still un-integrable (no reachable first call, endpoints showing only the `200` body, samples that contradict the schema). Judge whether a developer can *integrate from it*, not whether the *template is filled*.
- **The drift that reads consistent.** The reference and the api-spec can both look right in isolation while disagreeing — a field the reference shows that the contract never declared, an endpoint the contract dropped, an error the reference omits. The only way to catch it is to **trace documented endpoints/shapes/errors against the handed-in api-spec** (cond. 5). The single most damaging and most easily-missed defect.
- **The fabricated/orphan endpoint.** A reference can document an endpoint that looks plausible but the contract never declares. Spot-check the endpoint index against the api-spec one-to-one; an endpoint with no contract backing is a defect, not coverage.
- **Happy-path-only endpoints.** An endpoint block that shows the `200` body and stops reads complete but leaves the developer to discover failure modes by trial and error. Each operation needs its parameters, at least one worked example, and its error responses (cond. 2/3).
- **The sample that drifts from the schema — including after an amendment.** A curl or code sample using a field the contract doesn't carry (or a wrong type/status) breaks silently. On an amendment especially, a sample left unchanged after the schema changed reads as runnable but won't run (cond. 6/11).
- **Re-typed generated catalogs.** Where the endpoint catalog is generated from OpenAPI, a *hand-retyped* duplicate of it drifts immediately. A manually-maintained copy of a generated catalog is a drift hazard worth a finding (cond. 5); the generated catalog itself staying current is fine.
- **Pagination judged subjectively.** cond. 10 is structural — for a listing API, is the model / max / tie-broken sort documented? — not "is the pagination elegant." And it is **n/a** for a non-listing API; don't manufacture it.
- **Missing-contract blind spot.** If the api-spec wasn't handed in, the consistency dimension can't be fully run — do not let that absence default to an approve. Flag it (cond. 5 partially un-runnable) and judge the rest.
- **Systematic over-flagging (false-revise).** A reviewer asked to find problems tends to over-correct, judging sound references as defective. Calibrate to the bar: a condition is a gap only on a *named, real* deficiency, not on an organization or example you'd have written differently. Plausible-sounding nits are the dominant reviewer error.
- **False-revise on a proportionally-sized reference.** A thin API's reference is correctly small — a handful of endpoints, no pagination (cond. 10 n/a), a one-row changelog, no SDK table, no webhooks, no deprecation. That is right-sizing, not under-documentation. Manufacturing a gap from brevity drives avoidable revise loops; calibrate to the archetype (conditions 2 and 5 still bind).
- **Demanding a section for a surface the API doesn't have.** A REST-only API needs no webhook/GraphQL section; a non-listing API needs no pagination. The overlays are authoring aids — judge the outcome via the existing conditions, never a section demand (this is the inventing-conditions trap).
- **Confusing this with the user-guide, developer-guide, or design-review gate.** This judges the **published developer reference / endpoint catalog**. A user-guide-review judges end-user product help; a developer-guide-review judges the SDK/CLI adoption narrative; `reviewing-api-spec` gates the engineering *api-spec contract*. Don't apply an end-user, an adoption-narrative, or a wire-contract bar here.
- **Verdict token drift.** "Approved", "LGTM", "needs work", or a verdict buried mid-paragraph will not parse. Emit the literal `VERDICT: approve|revise` on its own line.

## Anti-patterns

- **Rubber-stamp approve.** Skimming and approving to avoid a revise loop — a fabricated endpoint, a drift from the contract, or a happy-path-only block waved through becomes a broken integration or a mid-build support ticket.
- **Skipping the api-spec trace.** "The reference looks internally consistent, so I'll approve" — without spot-checking against the handed-in contract you miss the highest-impact defect class (cond. 5). The one shortcut this gate exists to forbid.
- **Nit-pick revise.** Blocking on endpoint-ordering taste, wording preference, or nice-to-haves dressed up as gaps. Revise is for real usability/consistency blockers only.
- **Silent rewrite.** "It was easier to just fix the example" — authoring inside a review collapses the produce/judge separation and removes the author's chance to learn the gap.
- **Inventing conditions.** Adding a private requirement the bar does not carry ("it should also include a Postman collection / a GraphQL variant / an interactive try-it") drifts the review-bar off the produce-bar and causes spurious revises. Judge the eleven conditions only; the overlays/DX features are not conditions.
- **Maximalism.** Demanding pagination, a multi-language SDK matrix, webhooks, or a long changelog from a thin API that doesn't need them. The bar is the developer's ability to integrate, not the largest possible reference.
- **Full re-review of an amendment.** Re-judging the whole unchanged catalog on a delta instead of the delta-scoped path (cond. 11) — wasteful and off-protocol.
- **Hedged verdict.** "Mostly approve but…" or two verdict lines. Exactly one decision, exactly one token.

## Output

A single review result for one published (or amended) API reference:

- **One verdict line** — `VERDICT: approve` or `VERDICT: revise`, verbatim, on its own line.
- **Findings** — on `revise`, one actionable finding per blocking gap (failed condition + location + concrete fix); on `approve`, optional non-blocking notes.

The reference under review is **textual** today — endpoint sections + fenced request/response examples + fenced code samples (markdown via the local docs backend); the review **method + bar are medium-independent** (a future rendered docs site changes only the medium — and owns search/try-it/a11y/i18n — not what is judged). The **abstract consumer** is whatever orchestrates the produce->review loop: `approve` accepts the API reference for use by integrating developers; `revise` returns the findings to the producer for a bounded revision pass.

## Related

- An **api-reference-authoring** skill (`authoring-api-reference`) — the produce half of the pair; it writes the reference to the same 11-condition usability + contract-consistency bar this skill judges against. Pairing them single-sources the bar so produce and review do not drift.
- The upstream **api-spec** (`authoring-api-spec`) — the engineering wire contract every endpoint, field, event, and error in the reference derives from; this gate **checks the reference for consistency against the handed-in api-spec** (cond. 5). The api-spec itself is gated at engineering time by `reviewing-api-spec`, not here.
- A **user-guide-review** skill — the gate for the end-user product guide (the non-technical person using the product). Distinct doc/audience.
- A **developer-guide-review** skill — the gate for the SDK/CLI/platform adoption + integration narrative that *points into* this reference. Distinct doc/bar; this judges the endpoint catalog it links to.
- A **design-review** skill — the gate for generic engineering design documents (specs/plans/RFCs/ADRs). The upstream **engineering api-spec** wire contract has its own dedicated gate, `reviewing-api-spec` (design-review carves it out). Distinct gate/artifact; not for the published consumer reference.
- An **api-reference template / content-template** tool — owns the section *structure*; this skill judges *quality against the bar*, not structural conformance.

## Progressive disclosure

- `references/usability-consistency-bar.md` — per-condition pass/gap signals + worked findings for the deepened + new conditions (auth-flow depth, Problem-Details errors, RateLimit/idempotency, deprecation/sunset, pagination cond. 10, the delta-scoped amend cond. 11). Load when you need the detailed signal for a condition.
- `references/sources.md` — research provenance for the review method + the single-sourced bar. Load only to audit where the guidance came from.

## Body budget

- `description` <= 1,024 chars (agentskills.io cap). Claude truncates the combined `description` + `when_to_use` at 1,536 chars in the listing.
- Body <= ~500 lines / 5,000 tokens — kept in context every turn.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k tokens, error >50k.

## Changelog

- **1.1.0** (2026-06-14) — production-grade restructure (additive; single-sourced with `authoring-api-reference`'s Step-6 self-check). Bar 9 → **11 conditions**: added **cond-10** pagination/list-operation conventions (proportional) + **cond-11** delta-scoped amend (input-signal-gated, n/a greenfield); deepened cond-1 (auth-flow depth), cond-3 (RFC 9457 Problem Details + machine code), cond-4 (RateLimit-*/jitter/idempotency), cond-7 (Sunset/Deprecation mechanics + migration); cond-5 condition text kept VERBATIM (load-bearing) + checking method deepened (SSoT/contract-test, no hand-retyped catalog); cond-2 now includes contract-declared events/webhooks. API-style overlays + webhook-doc technique kept as AIDS judged by outcome; rendered-medium DX (search/try-it/a11y/i18n) scoped OUT. Added `references/usability-consistency-bar.md`; `sources.md` made portable. `VERDICT: approve|revise` + input contract unchanged.
- **1.0.0** (2026-06-05) — initial reviewed release.
