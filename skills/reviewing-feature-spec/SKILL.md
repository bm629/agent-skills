---
name: reviewing-feature-spec
description: >
  Use when reviewing/judging a finished feature specification to decide if
  engineering can plan and build from it — an acceptance gate, not authoring. Below
  the PRD. Judges it against a single-sourced
  10-condition implementability + testability bar: each feature traces to a PRD need
  (no orphans/gaps); behavior unambiguous + observable; I/O + states complete (a
  state-transition table where stateful); each edge case names its handling;
  acceptance criteria testable (Given/When/Then, or a metric-threshold for a
  probabilistic/ML feature); singular + consistent; load-bearing non-functional
  requirements carry numeric targets; an amend reviewed delta-scoped; open questions
  surfaced. EARS, decision tables, and archetype overlays are authoring aids judged
  by outcome, never demanded. Emits exactly `VERDICT: approve|revise` plus findings —
  approves a spec meeting the bar (no false-revise on a thin one), revises only on a
  real, named gap. Not for authoring, the upstream PRD, design docs (ADR/RFC), or
  other types.
extensions:
  claude:
    when_to_use: "judging a finished feature spec (greenfield or an amend) against the implementability + testability bar and emitting an approve/revise verdict"
    argument-hint: "<the finished feature spec to review, or the amended spec + its change request>"
version: "1.2.0"
forge:
  status: unreviewed
  forged: 2026-06-04
  reviewed: null
---

# `reviewing-feature-spec` — SKILL.md

> **Variant:** standard · **When to use:** judging a finished feature spec as an acceptance gate — checking it is implementable and testable, then emitting `VERDICT: approve|revise` with actionable findings. Greenfield, or an amend (delta-scoped).

## Overview

This skill is the *review* half of a producing/judging feature-spec pair. Loaded by a reviewer who holds a **finished feature specification** — the document below the PRD that says *how each feature behaves* — it judges that spec against one question: **can an engineer build it and a tester verify it without asking the author, so planning can cut tasks from it?** It applies a fixed **10-condition implementability + testability checklist** (the same bar a feature-spec author produces to, so the produce-bar and the review-bar do not drift), then emits a single machine-parseable verdict plus findings the author can act on in one revision pass. It is an acceptance gate — it does **not** author, fix, or rewrite the spec; it judges and returns findings, and the producer revises.

The bar is **single-sourced** with the author. The author's *techniques* — EARS phrasing, decision tables, use-case flow precision, archetype overlays, the 29148 vocabulary — are **aids the reviewer judges by OUTCOME** (is the behavior unambiguous? is the rule-set complete? are the AC testable for *this* feature's nature?), never conditions to demand. Minting a condition the author doesn't produce to (e.g. "must use EARS", "must have a UI section") is the cardinal drift this skill guards against.

## When to activate

- A finished feature spec needs an accept/revise decision before engineering plans or builds from it.
- You are the independent reviewer / gate for a feature spec a producer just authored.
- Re-judging a revised feature spec after a prior `revise` verdict.
- Reviewing an **amend** — an approved spec + a change request — as a delta-scoped review (cond-10).

**Do NOT activate when:**

- Authoring or repairing a feature spec → use a feature-spec-authoring skill. This skill never writes the spec.
- Reviewing the **upstream PRD** (the *what/why* product doc) → use a PRD-review skill. That gate judges product plannability; **this** gate judges per-feature implementability one layer down.
- Reviewing an **engineering design document** — architecture spec, design doc, ADR, or RFC → use a design-review skill. That gate verifies design claims against the codebase; this gate judges a behavior specification against an implementability bar.
- Checking template/section conformance → that is a template concern. This skill judges *quality against the bar*, not whether every heading is present.
- Reviewing any other document type.

## Workflow

### Step 1: Read the whole spec with fresh, independent eyes

Read the feature spec end to end as if encountering it for the first time, without the author's framing. Your stance is a gatekeeper for the *next* step (planning + build): a finding carries weight only when it shows the feature cannot be **built as written** or **tested as written**. Keep the upstream PRD (or the requirement list the spec decomposes) at hand — Step 2's first condition checks the spec against it both ways. **Is this an amend?** If you were handed a change request / delta against an existing spec, run the delta-scoped path (cond-10 active; scope the review to the changed blocks). On a greenfield first build no change request is present — cond-10 is n/a. Note where a behavior, input, edge case, acceptance criterion, state, or NFR is load-bearing; those are the spots the checklist scrutinizes.

### Step 2: Run the implementability + testability checklist — judge each condition

For each condition below, decide **pass** or **gap**. A condition fails only on a *real, named* deficiency — "I'd have phrased it differently" is not a gap. For each gap, capture the exact location and what is missing (Step 4 turns it into an actionable finding). The conditions are the single-sourced bar; do not add private ones.

1. **Traced to the upstream need.** Every feature maps back to a specific PRD goal / requirement / metric, and every upstream feature line is covered by a spec section — check **both directions**. A feature with no upstream line is an **orphan** (scope creep); an upstream line with no feature is a **coverage gap**. *Gap* on an orphan, an uncovered line, or unstated/unreconstructable traceability. *(Non-collapsing baseline — at any size a feature serving no PRD line is broken.)*
2. **Unambiguous + observable behavior.** Each behavior is interpretable exactly one way, stated as an **observable** system response, and **implementation-free**. Flows are coherent (a main success scenario; branches classified alternate-vs-exception). *Gap* when a behavior could be built two ways from the same words, has no observable output, smuggles in an implementation choice, or rests on a **load-bearing requirements-smell** (subjective/weak/ambiguous term, comparative without a referent, loophole, open-ended "etc."). *(Non-collapsing baseline.)*
3. **Complete inputs / outputs / states.** Every input enumerated with source, type, validation, required/optional; every output with shape/response + side effects; a **stateful** feature carries a **state-transition table** (every (state,event) cell a defined next-state or an explicit illegal-marker; initial/terminal named); a **combinatorial** feature's rule-set is complete (no input combination leaves the behavior undefined). *Gap* when a validation/output shape is missing, a stateful feature leaves transitions to guess, or a rule combination has no defined action. *(Collapse: a stateless feature has no state table; a non-combinatorial feature no decision table — not gaps.)*
4. **Edge cases + error handling present, each with its response.** The standard boundary/failure paths are addressed — null/empty, duplicate/idempotency, concurrency/race, permissions/visibility, limits/overflow (boundary-value at each limit) — and **each named edge case states its expected handling**. *Gap* when an applicable edge case is absent, or listed without saying what the system does. *(Collapse: a thin feature has a smaller failure surface — fewer edge cases is fine; the edge-carries-handling rule itself is a non-collapsing baseline.)*
5. **Independently testable acceptance criteria.** Each behavior + edge case carries pass/fail criteria a tester could execute **without asking the author** — Given/When/Then or a rule-based checklist. For a **probabilistic/ML** feature, a deterministic G/W/T mis-fits the output: a **metric-threshold criterion on a named dataset** (precision/recall/latency ≥ X) + the low-confidence/fallback behavior **is** testable and passes; a deterministic **"the model is accurate"/"results are relevant"** is the vague criterion this condition rejects. *Gap* on a vague/subjective criterion with no measurable pass/fail, or a behavior with no criterion. 4+ criteria in a section is a split smell — flag, not an auto-block. *(Non-collapsing baseline.)*
6. **Singular + consistent.** Each requirement states **one** idea (split an "and"), terminology is consistent, no internal contradictions. *Gap* on a compound requirement, a term that shifts meaning, or two sections that contradict. *(Collapse: a short spec has fewer surfaces — but consistency holds at any size.)*
7. **Feasible + plannable.** Buildable within stated constraints; inputs/outputs + criteria concrete enough that planning can cut tasks/milestones. *Gap* when a stated constraint makes a required behavior impossible, or the spec is too abstract to estimate/sequence.
8. **Open questions surfaced, not buried.** Genuine unknowns are stated openly, not papered as silent assumptions presented as settled fact. *Gap* when the spec reads as falsely complete — an obvious undecided point is absent or asserted as decided.
9. **Non-functional requirements present where the feature warrants them.** The **load-bearing** non-functional categories for the feature (performance, reliability/idempotency, security/authorization, privacy, accessibility WCAG 2.2 AA for UI, limits/quotas, compatibility) carry a **numeric/checkable target**; a vague "should be fast/secure" on a feature whose nature demands a target is a gap. *(Collapse: a trivial feature legitimately needs none; only the applicable few are expected — never demand a category the feature doesn't warrant. A deliberately best-effort NFR, stated as such, is not a gap.)*
10. **(Amend only) delta is well-scoped, ripple-clean, versioned.** When reviewing a change against an existing spec: the delta meets conditions 1–9 **on the blocks it touched**; the changed/added feature still traces to a PRD line (or an upstream-PRD-amend-needed is explicitly flagged); the document's own version is bumped + a changelog entry (who/when/what/why) present; superseded content is marked, not silently deleted; no internal or downstream trace is left dangling (the affected technical-design/test-plan/api-spec set is named). *Gap* on an un-scoped delta, a broken trace, missing change history, or a silent deletion. *(Collapse: on a greenfield first build this condition is n/a — do NOT full-re-review an unchanged spec, and do NOT demand a changelog on a first draft.)*

**Proportionality.** "Complete enough to build and test from" scales with the feature. A thin feature legitimately collapses sections it does not need — no states → no state table; no combinatorial logic → no decision table; no failure surface → fewer edge cases; trivial → no NFR; first draft → no changelog. Judge **completeness-of-decisions**, not word count or template-section presence. A small, complete spec that satisfies every *applicable* condition **passes**. Do not manufacture a gap from brevity.

### Step 3: Decide the verdict

- **approve** — every applicable condition passes. An engineer can build, and a tester can verify, this feature as written; planning can derive tasks from it. Approve even if you can imagine stylistic improvements; the bar is implementability + testability, not perfection.
- **revise** — one or more conditions have a real, named gap that blocks building or testing (an orphan feature, an ambiguous behavior, a missing edge-case response, an untestable criterion, an undefined state transition, a missing load-bearing NFR target, an un-scoped/ripple-broken amend, etc.).

Do not revise to signal effort or to request nice-to-haves. A condition is either met or it isn't.

### Step 4: Emit the verdict + actionable findings

Emit the verdict as a single line — the literal text `VERDICT: approve` or `VERDICT: revise`, on its own line, with **no** surrounding code fences, quotes, or extra words (the fences here are illustration only):

```
VERDICT: approve
```

Then, on the following lines, list findings. On `revise`, every finding is **actionable** — the failed condition, the exact location, and **how to fix it** — so the author can resolve it in one pass. On `approve`, findings are optional non-blocking notes; do not let them imply a revision is required.

A good finding names the gap and the fix:

> **revise** — Acceptance criteria (cond. 5), "Rank results" feature: the only criterion is "the relevance model is accurate," which a tester cannot run pass/fail. Fix: state a metric threshold on a named dataset, e.g. "on the 2026-Q2 holdout, precision@10 ≥ 0.80," plus the low-confidence fallback.

A bad finding is vague and unactionable:

> The acceptance criteria could be more thorough. *(Which feature? Why does it fail the bar? What fixes it?)*

## Rules

**Hard rules (never violate):**

- **Emit exactly one verdict line, `VERDICT: approve` or `VERDICT: revise`** — that literal token, on its own line, nothing else on it. Downstream tooling parses it.
- **Judge, never author.** Return findings; do not rewrite, fix, or fill in the spec. The producer revises.
- **Single-sourced bar.** Judge against the ten conditions in Step 2 — the same bar the author produces to. Do not invent extra conditions or apply a stricter private standard.
- **Aids are judged by outcome, never demanded.** EARS, decision tables, the use-case format, archetype overlays, the 29148 vocabulary are the author's *techniques* — judge whether the behavior is unambiguous / the rule-set complete / the AC testable, NEVER "you didn't use EARS / add a UI section / draw a decision table." This is the cardinal no-drift rule.
- **No false-revise.** A spec that meets every applicable condition is approved, even a thin one for a small feature. Revise only on a real, named gap. A thin feature legitimately omits NFRs, a state table, a decision table, a changelog.
- **No false-approve.** Never approve over a genuine gap to be agreeable. A blocking gap is a `revise`.
- **Edge case without a response is a gap (cond. 4).** The builder must not be left to invent the behavior.
- **Judge against the upstreams the document was given.** Assess the document against its `depends_on` set. A **not-produced** upstream is **never** a revise trigger. A document that **ignored a produced upstream** it should have drawn on **is** a fair finding.
- **Amend is delta-scoped.** When handed a change against an existing spec, review the delta + its ripple (cond-10) — do NOT full-re-review the unchanged spec, and do NOT demand a changelog on a greenfield first draft.
- **Every revise finding is actionable** — failed condition + location + concrete fix.

**Preferences (override-able):**

- Order findings by severity — blocking gaps first, then minor ones.
- Reference the condition number/name in each finding so the author maps it back to the bar.
- Keep approve-notes few and clearly non-blocking.

## Gotchas

- **Approving for completeness instead of buildability.** Every section can be present and the feature still un-buildable (ambiguous behavior, edge cases with no response, untestable criteria). Judge whether the *feature can be built and tested*, not whether the *template is filled*.
- **The listed-but-unhandled edge case.** A spec that *enumerates* null/empty, duplicate, concurrency, and limit cases looks thorough — but if it does not say **what the system does** for each, the build is still under-specified (cond. 4).
- **Deterministic bar on a probabilistic feature.** Don't reject a metric-threshold-on-a-dataset criterion for "not being Given/When/Then" — for a model/ranker that IS the testable form (cond. 5). Conversely, "the model is accurate" is a real gap.
- **Inventing conditions (the cardinal drift).** Adding a private requirement the bar does not carry ("it should use EARS / have a sequence diagram / a rollout plan / a UI section") drifts the review-bar off the produce-bar and causes spurious revises. The aids are judged by outcome only.
- **Systematic over-flagging (false-revise).** A reviewer asked to find problems tends to over-correct, judging sound specs as defective. A condition is a gap only on a *named, real* deficiency, not a sentence you'd have written differently.
- **False-revise on a thin feature.** A small feature's spec is correctly short; collapsed sections it doesn't need (no states, no NFR, no decision table, no changelog) are not gaps.
- **NFR/amend over-demand.** Don't demand an NFR category the feature doesn't warrant (cond. 9 is proportional), and don't apply cond-10 to a greenfield draft.
- **Confusing this with the PRD gate or design-review.** A feature spec is judged for per-feature implementability — one layer **below** the PRD's product plannability and distinct from an engineering design-doc's code-consistency review.
- **Verdict token drift.** "Approved", "LGTM", "needs work", or a verdict buried mid-paragraph will not parse. Emit the literal `VERDICT: approve|revise` on its own line.

## Anti-patterns

- **Rubber-stamp approve.** Skimming and approving to avoid a revise loop — an ambiguous behavior or an unhandled edge case waved through becomes a defect or a mid-build scramble.
- **Nit-pick revise.** Blocking on wording, formatting, or nice-to-haves dressed up as gaps. Revise is for real implementability/testability blockers only.
- **Silent rewrite.** "It was easier to just fix it" — authoring inside a review collapses the produce/judge separation.
- **Inventing conditions.** Adding a requirement the bar does not carry (a named technique, a section demand) — the dominant drift this gate guards against.
- **Full-re-reviewing an amend.** Re-judging the whole unchanged spec on a small delta — review the delta + its ripple (cond. 10), proportionally.
- **Hedged verdict.** "Mostly approve but…" or two verdict lines. Exactly one decision, exactly one token.

## Output

A single review result for one feature spec:

- **One verdict line** — `VERDICT: approve` or `VERDICT: revise`, verbatim, on its own line.
- **Findings** — on `revise`, one actionable finding per blocking gap (failed condition + location + concrete fix); on `approve`, optional non-blocking notes.

The abstract consumer is whatever orchestrates the produce→review loop: `approve` accepts the spec for the next phase (planning / build); `revise` returns the findings to the producer for a bounded revision pass.

## Related

- A **feature-spec-authoring** skill — the produce half of the pair; it writes the spec to the same 10-condition bar this skill judges against. Pairing them single-sources the bar so produce and review do not drift.
- A **PRD-review** skill — the gate one layer **up**, for the product requirements document (what/why). Distinct doc, distinct bar.
- A **design-review** skill — the gate for engineering design documents (architecture specs, ADRs, RFCs), which verifies claims against the codebase. Distinct gate, distinct bar.
- A **feature-spec template / content-template** tool — owns the section *structure*; this skill judges *quality against the bar*, not structural conformance.

## Progressive disclosure

- `references/implementability-bar.md` — the ten checklist conditions expanded with per-condition pass/gap signals, the standard edge-case checklist, the state-table + decision-table + probabilistic-AC + NFR + delta-scoped-amend signals, and worked finding examples. Load when a borderline condition needs a sharper pass/gap call.
- `references/sources.md` — research provenance for the review method (requirement-quality standards, EARS, BDD/Gherkin, INVEST, traceability, edge-case + probabilistic-AC + change-impact technique, reviewer-overcorrection evidence).

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap); combined `description` + `when_to_use` truncated at 1,536 chars in the listing.
- Body ≤ ~500 lines / 5,000 tokens — kept in context every turn.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k tokens, error >50k.
