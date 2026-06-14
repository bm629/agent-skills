---
name: reviewing-technical-design
description: >
  Use when reviewing/judging a finished technical-design document (a TDD /
  engineering design doc / design RFC) for one feature or component, to decide
  if an engineer can implement it without re-deriving the design — an acceptance
  gate, not authoring. Below the feature-spec. Judges it against a single-sourced
  11-condition implementability bar: every decision traces bidirectionally to a
  requirement (no orphan/gap); scoped to one feature within the architecture;
  the approach + component decomposition are implementable with a synced
  diagram+narration; interfaces/schemas an api-spec/data-model owns are
  referenced not duplicated (SSOT); at least one real alternative with a decision
  criterion; failure modes carry handling; observability signals named; testing
  covers the failures + contract conformance; rollout/migration/rollback with
  measurable triggers; assumptions explicit + nothing fabricated; an amend
  reviewed delta-scoped. FMEA/RTM/C4 are authoring aids judged by outcome, never
  demanded. Emits exactly `VERDICT: approve|revise` plus findings — approves a
  TDD meeting the bar (no false-revise on a thin one), revises only on a real,
  named gap. Not for authoring, the upstream PRD/feature-spec, the api-spec/
  data-model, or generic design docs/RFCs/ADRs (those use design-review).
extensions:
  claude:
    when_to_use: "judging a finished technical-design doc (greenfield or an amend) against the implementability bar and emitting an approve/revise verdict"
    argument-hint: "<the finished technical-design doc to review, or the amended TDD + its change request>"
version: "1.0.0"
forge:
  status: reviewed
  forged: 2026-06-14
  reviewed: 2026-06-14
---

# `reviewing-technical-design` — SKILL.md

> **Variant:** standard · **When to use:** judging a finished technical design doc as an acceptance gate — checking an engineer can implement it without re-deriving the design, then emitting `VERDICT: approve|revise` with actionable findings. Greenfield, or an amend (delta-scoped).

## Overview

This skill is the *review* half of a producing/judging technical-design pair. Loaded by a reviewer who holds a **finished technical design document (TDD)** — the document below the feature-spec that says *how one feature will be built* within an existing system — it judges that doc against one question: **can an engineer implement this feature without re-deriving the design, and is the chosen approach justified against a real alternative?** It applies a fixed **11-condition implementability checklist** (the same bar a TDD author produces to — `authoring-technical-design`'s Step-5 — so the produce-bar and the review-bar do not drift), then emits a single machine-parseable verdict plus findings the author can act on in one revision pass. It is an acceptance gate — it does **not** author, fix, or rewrite the design; it judges and returns findings, and the producer revises.

The bar is **single-sourced** with the author. The author's *techniques* — FMEA failure-mode analysis, the RTM trace matrix, C4 altitude framing, the choice of sequence vs flow diagram, pseudo-code form — are **aids the reviewer judges by OUTCOME** (is every decision traced? are failures handled? are signals named?), never conditions to demand. **But note the boundary:** rollout, observability, and testing ARE real, load-bearing conditions for a TDD (cond-7/8/9) — they are *not* "invented" conditions here the way a rollout demand would be for a feature-spec. What stays an aid is the *technique* (FMEA/RTM/C4/diagram-choice), not the *outcome* (a named signal, a traced decision, a rollback trigger).

## When to activate

- A finished technical design doc needs an accept/revise decision before an engineer implements from it.
- You are the independent reviewer / gate for a TDD a producer just authored.
- Re-judging a revised TDD after a prior `revise` verdict.
- Reviewing an **amend** — an approved TDD + a change request — as a delta-scoped review (cond-11).

**Do NOT activate when:**

- Authoring or repairing a TDD → use `authoring-technical-design`. This skill never writes the design.
- Reviewing the **upstream PRD or feature-spec** (what/why; how each feature behaves) → use a PRD-review / feature-spec-review skill. **This** gate judges *how the feature is built*, one layer down.
- Reviewing the **api-spec or data-model** themselves (the wire contract / the persisted schema) → those are their own documents this TDD references, with their own gates.
- Reviewing a **generic / ad-hoc engineering design doc, RFC, ADR, spec, or plan** (one not produced as the doc-library `technical-design` artifact) → use `design-review`, which verifies design claims against the codebase across all those types. **This** gate is for the doc-library technical-design artifact — identified **authoritatively** by the `template: technical-design` frontmatter; a `# Technical Design:` heading is a fallback signal only when frontmatter is absent (a generic doc that merely titles itself "Technical Design" without the stamp stays with `design-review`).
- Checking template/section conformance → that is a template concern. This skill judges *quality against the bar*, not whether every heading is present.

## Workflow

### Step 1: Read the whole design with fresh, independent eyes

Read the TDD end to end as if encountering it for the first time, without the author's framing. Your stance is a gatekeeper for the *next* step (implementation): a finding carries weight only when it shows the feature cannot be **built as designed** without re-deriving something the design should have settled. Keep the upstream feature-spec + PRD (and the architecture-doc / api-spec / data-model the TDD references) at hand — Step 2's first condition checks the design against the requirements both ways, and cond-4 checks that referenced contracts are not duplicated. **Is this an amend?** If you were handed a change request / delta against an existing TDD, run the delta-scoped path (cond-11 active; scope the review to the changed decisions + their ripple). On a greenfield first build no change request is present — cond-11 is n/a.

### Step 2: Run the implementability checklist — judge each condition

For each condition below, decide **pass** or **gap**. A condition fails only on a *real, named* deficiency — "I'd have designed it differently" is not a gap. For each gap, capture the exact location and what is missing (Step 4 turns it into an actionable finding). The conditions are the single-sourced bar; do not add private ones.

1. **Requirement trace complete + bidirectional.** Every requirement the feature must satisfy (PRD goal / feature-spec criterion / constraint) has a design element that satisfies it, and every non-trivial design decision traces back to a requirement — check **both directions**. A decision with no requirement is **scope creep / gold-plating**; a requirement with no design is a **coverage gap**. *Gap* on an orphan decision, an uncovered requirement, or unstated/unreconstructable traceability. *(Non-collapsing baseline — at any size a decision serving no requirement is broken.)*
2. **Scoped to one feature / right altitude.** The doc designs one feature/component *within* the existing architecture; system-wide structure is **referenced**, not redesigned. *Gap* when the TDD re-decides the topology / datastore / service boundaries (architecture work at the wrong altitude) instead of referencing the architecture-doc. *(Non-collapsing baseline.)*
3. **Approach + decomposition implementable.** A short approach overview; components/modules each with one responsibility + their collaborators, concrete enough to build; the primary control + data flow shown as a **diagram AND a numbered narration that agree**. *Gap* on a god-component, a box labelled only with the feature name, a flow with no diagram or a diagram that contradicts the prose. *(Collapse: a small feature has few components and a short flow.)*
4. **Reference-not-duplicate (SSOT).** Interfaces / schemas / topology an **api-spec / data-model / architecture-doc already owns** are **referenced with only the delta stated** — not inlined. *Gap* when the TDD pastes an endpoint list, a table DDL, or the service topology that an owning doc holds (guaranteed future drift). *(Collapse: a feature touching no owned contract has nothing to reference — not a gap.)*
5. **≥1 real alternative with a decision criterion.** At least one genuine (non-strawman) alternative a competent engineer might have chosen, compared via trade-offs, with the **decision criterion** that settled the choice stated. *Gap* on a single rubber-stamped option, a strawman ("do nothing / rewrite everything"), or a choice settled by assertion ("we picked the best") with no criterion. *(Non-collapsing baseline — the trade-off discipline holds at any size.)*
6. **Failure modes + cross-cutting robustness.** The significant failures (bad input, dependency failure/timeout, partial failure) are enumerated, **each with its detection + handling/recovery + user-visible effect**; the concurrency / ordering / idempotency stance is named where relevant; the security / scale / privacy surface is addressed where the feature has one. *Gap* on a happy-path-only design, a failure listed with no handling, or an unaddressed security/data surface the feature clearly has. *(Collapse: a thin feature has a smaller failure surface and may have no security/privacy/concurrency surface — fewer is fine; failure-carries-handling is itself a non-collapsing baseline.)*
7. **Observability addressed.** The health + failure **signals** the feature emits/monitors are named (a success/error metric, the key log/trace, the alert on the dominant failure mode) — the signals that also arm the rollback triggers. *Gap* on "we'll add logging later" for a production-facing feature, or a rollback (cond-9) with no signal behind its trigger. *(Collapse: a trivial internal helper keeps this brief — light is fine, absent-where-warranted is not.)*
8. **Testing addressed.** The verification approach is stated in testable terms — the unit/integration/e2e levels appropriate to the feature, **the failure cases from cond-6**, and **contract conformance** for any contract the feature exposes; it references the feature-spec's acceptance criteria rather than restating them. *Gap* on "we'll test it", a strategy that omits the failure cases, or an exposed contract with no conformance check. *(Collapse: a trivial feature may be unit-only; no exposed contract → no conformance check.)*
9. **Rollout / migration / rollback addressed.** How it ships (phasing / feature-flag / canary); the migration + backward-compat stance where data/contract changes; a rollback plan with **measurable triggers** (tied to the cond-7 signals, not "roll back if it looks bad"). *Gap* on an implied big-bang for a risky change, a data/contract change with no migration, or a rollback with no measurable trigger. *(Collapse: an internal additive feature has a trivial deploy and no migration — light is fine.)*
10. **Assumptions explicit + grounded, not fabricated.** Genuine unknowns are surfaced as assumptions / open questions, not papered as settled fact; the design reflects this feature's specifics and the real surrounding system; no approach/limit/interface is invented to look complete. *Gap* when the design reads as falsely complete, or asserts a limit/interface/approach that appears fabricated (no upstream or research behind it). *(Non-collapsing baseline.)*
11. **(Amend only) delta is well-scoped, ripple-clean, versioned.** When reviewing a change against an existing TDD: the delta meets conditions 1–10 **on the decisions it touched**; the changed decision still traces to a requirement (or an upstream-PRD/feature-spec-amend-needed is explicitly flagged); the **SSOT ripple** is handled (if a contract changed, the owning api-spec/data-model amend + the downstream impl/test-plan/runbook re-point are named); the doc's own version is bumped + a changelog (who/when/what/why) present; superseded decisions are marked, not silently deleted. *Gap* on an un-scoped delta, a broken trace, an un-flagged SSOT ripple, missing change history, or a silent deletion. *(Collapse: on a greenfield first build this condition is n/a — do NOT full-re-review an unchanged TDD, and do NOT demand a changelog on a first draft.)*

**Proportionality.** "Implementable without re-deriving the design" scales with the feature. A thin feature legitimately collapses what it does not need — no concurrency → no concurrency stance; nothing persisted → no migration; trivial internal helper → light observability; no exposed contract → no conformance test; first draft → no changelog. Judge **completeness-of-decisions**, not word count or template-section presence. A small, complete design that satisfies every *applicable* condition **passes**. Do not manufacture a gap from brevity.

### Step 3: Decide the verdict

- **approve** — every applicable condition passes. An engineer can implement this feature as designed, without re-deriving the design; the chosen approach is justified. Approve even if you can imagine stylistic improvements; the bar is implementability, not perfection.
- **revise** — one or more conditions have a real, named gap that blocks implementation (an orphan decision, a mis-scoped redesign, an inlined api-spec contract, a single un-weighed option, a failure with no handling, no observability on a production feature, a strategy missing the failure cases, a rollback with no measurable trigger, an un-scoped/ripple-broken amend, etc.).

Do not revise to signal effort or to request nice-to-haves. A condition is either met or it isn't.

### Step 4: Emit the verdict + actionable findings

Emit the verdict as a single line — the literal text `VERDICT: approve` or `VERDICT: revise`, on its own line, with **no** surrounding code fences, quotes, or extra words (the fences here are illustration only):

```
VERDICT: approve
```

Then, on the following lines, list findings. On `revise`, every finding is **actionable** — the failed condition, the exact location, and **how to fix it** — so the author can resolve it in one pass. On `approve`, findings are optional non-blocking notes; do not let them imply a revision is required.

A good finding names the gap and the fix:

> **revise** — Reference-not-duplicate (cond. 4), §5 Interfaces: the full `GET /reports` endpoint list (params, response schema) is pasted from the api-spec. Fix: reference `api-spec §Reports` and state only this feature's delta (the new `format=csv` param), so the contract has one source of truth.

A bad finding is vague and unactionable:

> The interfaces section could be tightened up. *(Which contract? Why does it fail the bar? What fixes it?)*

## Rules

**Hard rules (never violate):**

- **Emit exactly one verdict line, `VERDICT: approve` or `VERDICT: revise`** — that literal token, on its own line, nothing else on it. Downstream tooling parses it.
- **Judge, never author.** Return findings; do not rewrite, fix, or fill in the design. The producer revises.
- **Single-sourced bar.** Judge against the eleven conditions in Step 2 — the same bar the author (`authoring-technical-design` Step-5) produces to. Do not invent extra conditions or apply a stricter private standard.
- **Aids are judged by outcome, never demanded.** FMEA, the RTM matrix, C4 altitude language, the sequence-vs-flow diagram choice, pseudo-code form are the author's *techniques* — judge whether the decision is traced / the failure handled / the signal named, NEVER "you didn't use FMEA / draw an RTM / use a sequence diagram." (Rollout/observability/testing OUTCOMES are real conditions cond-7/8/9 — only the techniques are aids.)
- **No false-revise.** A design that meets every applicable condition is approved, even a thin one for a small feature. Revise only on a real, named gap. A thin feature legitimately omits migration, concurrency, a separate observability section, a changelog.
- **No false-approve.** Never approve over a genuine gap to be agreeable. A blocking gap is a `revise`.
- **Failure without handling is a gap (cond. 6).** The builder must not be left to invent the recovery.
- **Reference-not-duplicate is load-bearing (cond. 4).** An inlined contract another doc owns is a real gap (drift), not a style nit.
- **Judge against the upstreams the document was given.** Assess the TDD against its `depends_on` set + the docs it references. A **not-produced** upstream is **never** a revise trigger. A TDD that **ignored a produced upstream** it should have referenced **is** a fair finding.
- **Amend is delta-scoped.** When handed a change against an existing TDD, review the delta + its ripple (cond-11) — do NOT full-re-review the unchanged design, and do NOT demand a changelog on a greenfield first draft.
- **Every revise finding is actionable** — failed condition + location + concrete fix.

**Preferences (override-able):**

- Order findings by severity — blocking gaps first, then minor ones.
- Reference the condition number/name in each finding so the author maps it back to the bar.
- Keep approve-notes few and clearly non-blocking.

## Gotchas

- **Approving for completeness instead of buildability.** Every section can be present and the feature still un-buildable (an ambiguous decomposition, failures with no handling, an inlined contract that will drift). Judge whether the *feature can be implemented without re-deriving the design*, not whether the *template is filled*.
- **The listed-but-unhandled failure.** A design that *enumerates* bad-input, timeout, and partial-failure looks thorough — but if it does not say **detection + handling/recovery** for each, the build is still under-specified (cond. 6).
- **Strawman alternatives waved through.** "Alternative: do nothing" is not a real trade-off; cond-5 needs a genuine option a competent engineer might have chosen + the criterion that ruled it out.
- **Treating rollout/observability/testing as invented conditions.** For a *feature-spec* a rollout demand would be inventing a condition — but for a *TDD* these are the bar (cond-7/8/9). Do not under-review them by mis-importing the feature-spec reviewer's stance.
- **Inventing conditions (the cardinal drift).** Adding a private requirement the bar does not carry ("you must use FMEA / draw an RTM matrix / use a sequence diagram not a flowchart") drifts the review-bar off the produce-bar. The techniques are judged by outcome only.
- **Systematic over-flagging (false-revise).** A reviewer asked to find problems tends to over-correct. A condition is a gap only on a *named, real* deficiency, not a decision you'd have made differently.
- **False-revise on a thin feature.** A small feature's TDD is correctly short; collapsed sections it doesn't need (no migration, no concurrency, no separate observability, no changelog) are not gaps.
- **Confusing this with the feature-spec gate or design-review.** A TDD is judged for *how the feature is built* — one layer **below** the feature-spec's behavior, and distinct from `design-review` (which gates generic design docs/RFCs/ADRs/specs/plans by verifying claims against the codebase). This gate is the doc-library technical-design artifact's dedicated reviewer.
- **Verdict token drift.** "Approved", "LGTM", "needs work", or a verdict buried mid-paragraph will not parse. Emit the literal `VERDICT: approve|revise` on its own line.

## Anti-patterns

- **Rubber-stamp approve.** Skimming and approving to avoid a revise loop — an inlined contract or an unhandled failure waved through becomes a defect or a mid-build scramble.
- **Nit-pick revise.** Blocking on wording, diagram style, or nice-to-haves dressed up as gaps. Revise is for real implementability blockers only.
- **Silent rewrite.** "It was easier to just fix the design" — authoring inside a review collapses the produce/judge separation.
- **Inventing conditions.** Adding a requirement the bar does not carry (a named technique, a diagram-type demand) — the dominant drift this gate guards against.
- **Full-re-reviewing an amend.** Re-judging the whole unchanged design on a small delta — review the delta + its ripple (cond. 11), proportionally.
- **Hedged verdict.** "Mostly approve but…" or two verdict lines. Exactly one decision, exactly one token.

## Output

A single review result for one technical design doc:

- **One verdict line** — `VERDICT: approve` or `VERDICT: revise`, verbatim, on its own line.
- **Findings** — on `revise`, one actionable finding per blocking gap (failed condition + location + concrete fix); on `approve`, optional non-blocking notes.

The abstract consumer is whatever orchestrates the produce→review loop: `approve` accepts the design for implementation; `revise` returns the findings to the producer for a bounded revision pass. **Medium:** the artifact judged is a **textual-markdown** TDD today; the bar is medium-independent.

## Related

- **`authoring-technical-design`** — the produce half of the pair; it writes the design to the same 11-condition bar this skill judges against. Pairing them single-sources the bar so produce and review do not drift.
- A **feature-spec-review** skill — the gate one layer **up**, for the feature specification (how each feature behaves). Distinct doc, distinct bar.
- A **`design-review`** skill — the gate for *generic* engineering design docs, RFCs, ADRs, specs, and plans (it verifies claims against the codebase). This skill is the dedicated reviewer for the doc-library **technical-design** artifact; `design-review` does not gate that artifact.
- An **api-spec / data-model**, where they exist — the contracts the TDD references; cond-4 checks they are referenced, not duplicated, here.
- A **technical-design template / content-template** tool — owns the section *structure*; this skill judges *quality against the bar*, not structural conformance.

## Progressive disclosure

- `references/implementability-bar.md` — the eleven checklist conditions expanded with per-condition pass/gap signals and worked finding examples (the bidirectional trace, the SSOT/reference-not-duplicate check, the real-alternative-with-criterion test, the failure-with-handling table, the observability signal taxonomy, the test/conformance signals, the rollout/measurable-rollback signals, and the delta-scoped-amend signals). Load when a borderline condition needs a sharper pass/gap call.
- `references/sources.md` — research provenance for the review method (design-doc/RFC practice, FMEA, RTM/traceability, single-source-of-truth, observability, RFC/ADR amend lifecycle).

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap); combined `description` + `when_to_use` truncated at 1,536 chars in the listing.
- Body ≤ ~500 lines / 5,000 tokens — kept in context every turn.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k tokens, error >50k.
