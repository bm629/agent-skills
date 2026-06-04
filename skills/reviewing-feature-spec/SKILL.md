---
name: reviewing-feature-spec
description: >
  Use when reviewing or judging a finished feature specification to decide whether
  engineering can plan and build from it — an acceptance gate, not
  authoring. The feature spec is the layer below the PRD — it says how each feature
  behaves, in enough detail to build and test. Judges it against an implementability +
  testability bar: every feature traces to an upstream PRD need (no orphans, no coverage
  gaps), behavior is unambiguous and observable, inputs/outputs/states are complete,
  every edge case names its expected response, acceptance criteria are independently
  testable (Given/When/Then or rule-based), and open questions are surfaced. Emits
  exactly `VERDICT: approve|revise` plus actionable findings (failed condition + how to
  fix). Approves a spec that meets the bar (no false-revise) and revises only on a real,
  named gap. Not for authoring a spec, not for the upstream PRD (use a PRD-review skill),
  not for engineering design docs like ADRs/RFCs (use design-review), and not for other
  document types.
extensions:
  claude:
    when_to_use: "judging a finished feature spec against the implementability + testability bar and emitting an approve/revise verdict"
    argument-hint: "<the finished feature spec to review>"
version: "1.1.0"
forge:
  status: reviewed
  forged: 2026-06-04
  reviewed: 2026-06-04
---

# `reviewing-feature-spec` — SKILL.md

> **Variant:** standard · **When to use:** judging a finished feature spec as an acceptance gate — checking it is implementable and testable, then emitting `VERDICT: approve|revise` with actionable findings.

## Overview

This skill is the *review* half of a producing/judging feature-spec pair. Loaded by a reviewer who holds a **finished feature specification** — the document below the PRD that says *how each feature behaves* — it judges that spec against one question: **can an engineer build it and a tester verify it without asking the author, so planning can cut tasks from it?** It applies a fixed **implementability + testability checklist** (the same bar a feature-spec author produces to, so the produce-bar and the review-bar do not drift), then emits a single machine-parseable verdict plus findings the author can act on in one revision pass. It is an acceptance gate — it does **not** author, fix, or rewrite the spec; it judges and returns findings, and the producer revises.

## When to activate

- A finished feature spec needs an accept/revise decision before engineering plans or builds from it.
- You are the independent reviewer / gate for a feature spec a producer just authored.
- Re-judging a revised feature spec after a prior `revise` verdict.

**Do NOT activate when:**

- Authoring or repairing a feature spec → use a feature-spec-authoring skill. This skill never writes the spec.
- Reviewing the **upstream PRD** (the *what/why* product doc) → use a PRD-review skill. That gate judges product plannability; **this** gate judges per-feature implementability one layer down.
- Reviewing an **engineering design document** — an architecture spec, design doc, ADR, or RFC → use a design-review skill. That gate verifies design claims against the codebase; this gate judges a behavior specification against an implementability bar.
- Checking template/section conformance → that is a template concern. This skill judges *quality against the bar*, not whether every heading is present.
- Reviewing any other document type.

## Workflow

### Step 1: Read the whole spec with fresh, independent eyes

Read the feature spec end to end as if encountering it for the first time, without the author's framing. Your stance is a gatekeeper for the *next* step (planning + build): a finding carries weight only when it shows the feature cannot be **built as written** or **tested as written**. Keep the upstream PRD (or the requirement list the spec decomposes) at hand — Step 2's first condition checks the spec against it both ways. Note where a behavior, input, edge case, or acceptance criterion is load-bearing; those are the spots the checklist scrutinizes.

### Step 2: Run the implementability + testability checklist — judge each condition

For each condition below, decide **pass** or **gap**. A condition fails only on a *real, named* deficiency — "I'd have phrased it differently" is not a gap. For each gap, capture the exact location and what is missing (Step 4 turns it into an actionable finding). The conditions are the single-sourced bar; do not add private ones.

1. **Traced to the upstream need.** Every feature in the spec maps back to a specific PRD goal / requirement / metric, and every upstream feature line is covered by a spec section. Check **both directions**: a feature with no upstream line behind it is an **orphan** (scope creep); an upstream line with no feature is a **coverage gap**. *Gap* when an orphan or an uncovered upstream line exists, or when traceability is simply unstated and cannot be reconstructed.
2. **Unambiguous + observable behavior.** Each behavior is interpretable in exactly one way, stated as an **observable** system response to an input/interaction, and **implementation-free** (what the system does, not how it is coded). *Gap* when a behavior could be built two different ways from the same words, is described only internally (no observable output a tester could see), or smuggles in an implementation choice the spec has no business fixing.
3. **Complete inputs / outputs / states.** Every input is enumerated with its source, type, validation rule, and required/optional status; every output is enumerated with its shape/response and side effects; and if the feature is **stateful**, its states and the legal (and illegal) transitions are listed. *Gap* when an input's validation or an output's shape is missing, or a stateful feature leaves transitions unspecified so a builder must guess.
4. **Edge cases + error handling present, each with its response.** The standard boundary/failure paths are addressed — null/empty, duplicate/idempotency, concurrency/race, permissions/visibility, limits/overflow — and **each named edge case states its expected handling or error response**, not merely that it exists. *Gap* when an applicable edge case is absent, or is listed without saying what the system should do — a bare "handle duplicates" with no defined response is still a gap, because the builder is left to invent the behavior.
5. **Independently testable acceptance criteria.** Each behavior and edge case carries pass/fail criteria a tester could execute **without asking the author** — preferably Given/When/Then (a context, an action, an observable result) or a rule-based checklist. *Gap* when a criterion is vague or subjective ("fast", "user-friendly", "works well") with no measurable pass/fail, or a behavior has no criterion at all. A section with **four or more** acceptance criteria is a smell that two features are fused — flag it to split, not as an automatic block.
6. **Singular + consistent.** Each requirement states **one** idea (split a requirement joined by "and" into two), terminology is consistent across sections, and there are no internal contradictions. *Gap* on a compound requirement, a term that shifts meaning between sections, or two sections that contradict.
7. **Feasible + plannable.** The feature is buildable within the spec's stated constraints, and its inputs/outputs + acceptance criteria are concrete enough that planning can cut tasks/milestones from them. *Gap* when a behavior the stated constraints make impossible is required, or when the spec is too abstract for a planner to estimate or sequence the work.
8. **Open questions surfaced, not buried.** Genuine unknowns and unresolved decisions are stated openly, not papered over as silent assumptions presented as settled fact. *Gap* when the spec reads as falsely complete — an obvious undecided point is absent or is asserted as decided when it plainly is not.

**Proportionality.** "Complete enough to build and test from" scales with the feature. A thin feature legitimately collapses sections it does not need — no states → no state section; no failure surface → fewer edge cases. Judge **completeness-of-decisions**, not word count. A small, complete spec that satisfies every *applicable* condition **passes**. Do not manufacture a gap from brevity.

### Step 3: Decide the verdict

- **approve** — every applicable condition passes. An engineer can build, and a tester can verify, this feature as written; planning can derive tasks from it. Approve even if you can imagine stylistic improvements; the bar is implementability + testability, not perfection.
- **revise** — one or more conditions have a real, named gap that blocks building or testing (an orphan feature, an ambiguous behavior, a missing edge-case response, an untestable criterion, etc.).

Do not revise to signal effort or to request nice-to-haves. A condition is either met or it isn't.

### Step 4: Emit the verdict + actionable findings

Emit the verdict as a single line — the literal text `VERDICT: approve` or `VERDICT: revise`, on its own line, with **no** surrounding code fences, quotes, or extra words (the fences here are illustration only):

```
VERDICT: approve
```

Then, on the following lines, list findings. On `revise`, every finding is **actionable** — the failed condition, the exact location, and **how to fix it** — so the author can resolve it in one pass. On `approve`, findings are optional non-blocking notes; do not let them imply a revision is required.

A good finding names the gap and the fix:

> **revise** — Edge cases (cond. 4), "Submit order" section: the duplicate-submission case is listed but no expected response is given. Fix: state the handling, e.g. "a second submit of the same idempotency key returns the original order and does not create a second order."

A bad finding is vague and unactionable:

> The error handling could be more thorough. *(Which case? Why does it fail the bar? What fixes it?)*

## Rules

**Hard rules (never violate):**

- **Emit exactly one verdict line, `VERDICT: approve` or `VERDICT: revise`** — that literal token, on its own line, nothing else on it. Downstream tooling parses it.
- **Judge, never author.** Return findings; do not rewrite, fix, or fill in the spec. The producer revises.
- **Single-sourced bar.** Judge against the eight conditions in Step 2 — the same bar the author produces to. Do not invent extra conditions or apply a stricter private standard.
- **No false-revise.** A spec that meets every applicable condition is approved, even a thin one for a small feature. Revise only on a real, named gap.
- **No false-approve.** Never approve over a genuine gap to be agreeable. A blocking gap is a `revise`.
- **Edge case without a response is a gap.** Listing an edge case but not its expected handling fails condition 4 — the builder must not be left to invent the behavior.
- **Judge against the upstreams the document was given.** Assess the document against its `depends_on` set (the upstream documents the project actually produced). A **not-produced** upstream is **never** a revise trigger — never invent an expectation of a document the project didn't make. But a document that **ignored a produced upstream** it should have drawn on (e.g. a `depends_on` feature-spec whose behaviors the flows don't reflect) **is** a fair finding.
- **Every revise finding is actionable** — failed condition + location + concrete fix. No vague notes.

**Preferences (override-able):**

- Order findings by severity — blocking gaps first, then minor ones.
- Reference the condition number/name in each finding so the author maps it back to the bar.
- Keep approve-notes few and clearly non-blocking.

## Gotchas

- **Approving for completeness instead of buildability.** Every section can be present and the feature still un-buildable (ambiguous behavior, edge cases with no defined response, untestable criteria). Judge whether the *feature can be built and tested*, not whether the *template is filled*.
- **The listed-but-unhandled edge case.** A spec that *enumerates* null/empty, duplicate, concurrency, and limit cases looks thorough — but if it does not say **what the system does** for each, the build is still under-specified. Presence of the case is not handling of the case (cond. 4).
- **Systematic over-flagging (false-revise).** A reviewer asked to find problems — especially one also asked to propose fixes — tends to over-correct, judging sound specs as defective. Calibrate to the bar: a condition is a gap only on a *named, real* deficiency, not on a sentence you would have written differently. Plausible-sounding nits are the dominant reviewer error here.
- **False-revise on a thin feature.** A small feature's spec is correctly short; collapsed sections it does not need (no states, few edge cases) are not gaps. Manufacturing a gap from brevity drives avoidable revise loops — calibrate to the feature's surface area.
- **Confusing this with the PRD gate or design-review.** A feature spec is judged for per-feature implementability — one layer **below** the PRD's product plannability and distinct from an engineering design-doc's code-consistency review. Don't apply the upstream PRD bar or a spec/ADR/RFC bar to it.
- **Verdict token drift.** "Approved", "LGTM", "needs work", or a verdict buried mid-paragraph will not parse. Emit the literal `VERDICT: approve|revise` on its own line.

## Anti-patterns

- **Rubber-stamp approve.** Skimming and approving to avoid a revise loop — the gate exists to catch un-buildable specs; an ambiguous behavior or an unhandled edge case waved through becomes a defect or a mid-build clarification scramble.
- **Nit-pick revise.** Blocking on wording, formatting, or nice-to-haves dressed up as gaps. Revise is for real implementability/testability blockers only.
- **Silent rewrite.** "It was easier to just fix it" — authoring inside a review collapses the produce/judge separation and removes the author's chance to learn the gap.
- **Inventing conditions.** Adding a private requirement the bar does not carry ("it should also have sequence diagrams / a rollout plan") drifts the review-bar off the produce-bar and causes spurious revises.
- **Hedged verdict.** "Mostly approve but…" or two verdict lines. Exactly one decision, exactly one token.

## Output

A single review result for one feature spec:

- **One verdict line** — `VERDICT: approve` or `VERDICT: revise`, verbatim, on its own line.
- **Findings** — on `revise`, one actionable finding per blocking gap (failed condition + location + concrete fix); on `approve`, optional non-blocking notes.

The abstract consumer is whatever orchestrates the produce→review loop: `approve` accepts the spec for the next phase (planning / build); `revise` returns the findings to the producer for a bounded revision pass.

## Related

- A **feature-spec-authoring** skill — the produce half of the pair; it writes the spec to the same implementability + testability bar this skill judges against. Pairing them single-sources the bar so produce and review do not drift.
- A **PRD-review** skill — the gate one layer **up**, for the product requirements document (what/why). Distinct doc, distinct bar; not used for the feature spec.
- A **design-review** skill — the gate for engineering design documents (architecture specs, design docs, ADRs, RFCs), which verifies claims against the codebase. Distinct gate, distinct bar; not used for a behavior spec.
- A **feature-spec template / content-template** tool — owns the section *structure*; this skill judges *quality against the bar*, not structural conformance.

## Progressive disclosure

- `references/implementability-bar.md` — the eight checklist conditions expanded with per-condition pass/gap signals, the standard edge-case checklist, and worked finding examples. Load when a borderline condition needs a sharper pass/gap call.
- `references/sources.md` — research provenance for the review method (requirement-quality standards, inspection/traceability technique, testability and edge-case checklists, reviewer-overcorrection evidence).

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap). Claude truncates the combined `description` + `when_to_use` at 1,536 chars in the listing.
- Body ≤ ~500 lines / 5,000 tokens — kept in context every turn.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k tokens, error >50k.
