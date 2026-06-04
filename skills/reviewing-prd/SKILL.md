---
name: reviewing-prd
description: >
  Use when reviewing or judging a finished PRD (product requirements document) to
  decide whether the downstream build can be planned from it — an acceptance gate,
  not authoring. Judges the PRD against a plannability bar: the problem is evidenced
  (not asserted), users/personas are concrete, success metrics are measurable, the
  MVP boundary is explicit and defensible, the feature set and acceptance criteria
  are concrete enough to derive milestones from, no evidence is fabricated, and open
  questions are surfaced. Emits exactly `VERDICT: approve|revise` plus actionable
  findings (the failed condition + how to fix it). Approves a PRD that meets the bar
  (no false-revise) and revises only on a real, named gap. Not for authoring or
  fixing a PRD, not for reviewing engineering design docs (specs, ADRs, RFCs), and
  not for other document types.
extensions:
  claude:
    when_to_use: "judging a finished PRD against the plannability bar and emitting an approve/revise verdict"
    argument-hint: "<the finished PRD to review>"
version: "1.0.0"
forge:
  status: reviewed
  forged: 2026-06-04
  reviewed: 2026-06-04
---

# `reviewing-prd` — SKILL.md

> **Variant:** standard · **When to use:** judging a finished PRD as an acceptance gate — checking it is plannable, then emitting `VERDICT: approve|revise` with actionable findings.

## Overview

This skill is the *review* half of a producing/judging PRD pair. Loaded by a reviewer who has a **finished PRD** in hand, it judges that PRD against one question: **can the downstream build be planned from it?** It applies a fixed **plannability checklist** (the same bar a PRD author produces to, so the produce-bar and review-bar do not drift), detects fabricated evidence, then emits a single machine-parseable verdict plus findings the author can act on in one revision pass. It is an acceptance gate — it does **not** author, fix, or rewrite the PRD; it judges and returns findings, and the producer revises.

## When to activate

- ✅ A finished PRD needs an accept/revise decision before downstream planning begins.
- ✅ You are the independent reviewer / gate for a PRD a producer just authored.
- ✅ Re-judging a revised PRD after a prior `revise` verdict.

**Do NOT activate when:**

- Authoring or repairing a PRD → use a PRD-authoring skill. This skill never writes the PRD.
- Reviewing an engineering design document — a spec, plan, design doc, ADR, or RFC → use a design-review skill. That gate verifies engineering claims against the codebase; **this** gate judges product plannability and is **not** used for the PRD's engineering siblings.
- Checking template/section conformance → that is a template concern. This skill judges *quality against the bar*, not whether every heading is present.
- Reviewing any other document type.

## Workflow

### Step 1: Read the whole PRD with fresh, independent eyes

Read the PRD end to end as if encountering it for the first time, without the author's framing. Your stance is a gatekeeper for the *next* step (planning): findings carry weight only when they show the build cannot be planned as written. Note where a claim, metric, or scope line is load-bearing — those are the spots Step 2 scrutinizes.

### Step 2: Run the plannability checklist — judge each condition

For each condition below, decide **pass** or **gap**. A condition fails only on a *real, named* deficiency — "I'd have phrased it differently" is not a gap. For each gap, capture the exact location and what is missing (Step 4 turns it into an actionable finding).

1. **Problem evidenced, not asserted.** The problem is backed by evidence — qualitative signals (user interviews, support tickets, feedback) and/or quantitative data (conversion, churn, drop-off rates) — and is sized concretely (e.g. "drop-off at step 3 affects 42% of new accounts"). *Gap* when the problem is a bare assertion ("users want this"), or evidence is vague/hand-waved with no source, magnitude, or who-is-affected.
2. **Users/personas concrete.** At least the primary persona(s) with real needs and scenarios (user stories: "As a … I want … so that …"). *Gap* when users are a generic "the user" with no needs or scenarios a planner could design against.
3. **Measurable success metrics.** Up to ~4 outcome metrics (a few that matter — **one can suffice for a thin project**), **each** with a **target value** and a **measurement method** (how it is instrumented/tracked). *Gap* when a metric has no target, no way to measure it, or is a vanity metric (impressions, raw signups) untied to user value or business impact. A metric dump (ten unprioritized KPIs) is also a gap — the bar is a few that matter, not many. Do **not** revise a thin PRD for having a single good metric.
4. **Defensible MVP boundary.** An explicit in-scope vs out-of-scope split, named **non-goals**, and **release criteria** (the definition of done for first launch). *Gap* when scope is fuzzy/everything-in-v1, non-goals are absent (without an out-of-scope list, everything is in scope), or there is no stated bar for "ready to ship."
5. **Concrete, plannable features.** A feature set plus **acceptance criteria** specific enough that an engineer can derive milestones/tasks. Acceptance criteria must be independently testable — clear pass/fail, no room for interpretation (Given/When/Then is a strong sign). *Gap* when features are abstract goals with no testable "done," so a planner cannot estimate or sequence them.
6. **No fabricated evidence.** Every citation, statistic, and research figure must be real and verifiable, **or** be honestly flagged as an assumption to validate before build. Treat precise-but-unsourced numbers, named studies you cannot trace, and suspiciously round/confident figures as suspect — AI-authored PRDs fabricate plausible-looking citations and data at a high rate. *Gap* (and a serious one) when evidence appears invented and is presented as fact; flag the specific claim and demand a real source or its down-grade to a stated assumption. An honestly-labelled assumption ("assumed, validate pre-build") is **not** a gap — only evidence dressed up as fact it isn't. **Never let a fabricated number pass as fact.**
7. **Open questions + risks surfaced, not hidden.** Genuine unknowns and risks are stated openly (risks with likelihood/impact + mitigation; open questions listed), not buried or papered over. *Gap* when the PRD reads as falsely complete — obvious unknowns absent, or a stated assumption presented as settled fact.
8. **Clear and unambiguous.** Language is jargon-free and terminology consistent, so a cross-functional reader interprets each requirement one way. *Gap* when ambiguity would make two planners build two different things.

**Proportionality.** "Concrete enough to plan from" scales with the project. A thin project legitimately collapses sections it does not need — a small, complete PRD that satisfies every applicable condition **passes**. Judge completeness-of-decisions, not word count. Do not manufacture a gap from brevity.

### Step 3: Decide the verdict

- **approve** — every applicable condition passes. The build can be planned from this PRD as written. Approve it even if you can imagine stylistic improvements; the bar is plannability, not perfection.
- **revise** — one or more conditions have a real, named gap that blocks planning (a missing target on a metric, no non-goals, an abstract feature with no testable done, a fabricated statistic, etc.).

Do not revise to signal effort or to request nice-to-haves. A condition is either met or it isn't.

### Step 4: Emit the verdict + actionable findings

Emit the verdict as a single line — the literal text `VERDICT: approve` or `VERDICT: revise`, on its own line, with **no** surrounding code fences, quotes, or extra words (the fences here are illustration only):

```
VERDICT: approve
```

Then, on the following lines, list findings. On `revise`, every finding is **actionable** — the failed condition, the exact location, and **how to fix it** — so the author can resolve it in one pass. On `approve`, findings are optional non-blocking notes; do not let them imply a revision is required.

A good finding names the gap and the fix:

> **revise** — Success metrics (cond. 3): "improve onboarding" has no target or measurement method. Fix: state a target and how it's tracked, e.g. "step-3 completion ≥ 70%, measured via the onboarding funnel event."

A bad finding is vague and unactionable:

> The metrics section could be stronger. *(Which metric? Why does it fail? What fixes it?)*

## Rules

**Hard rules (never violate):**

- **Emit exactly one verdict line, `VERDICT: approve` or `VERDICT: revise`** — that literal token, on its own line, nothing else on it. Downstream tooling parses it.
- **Judge, never author.** Return findings; do not rewrite, fix, or fill in the PRD. The producer revises.
- **Single-sourced bar.** Judge against the eight plannability conditions in Step 2 — the same bar the author produces to. Do not invent extra conditions or a stricter private standard.
- **No false-revise.** A PRD that meets every applicable condition is approved, even a thin one for a small project. Revise only on a real, named gap.
- **No false-approve.** Never approve over a genuine gap to be agreeable. A blocking gap is a `revise`.
- **Fabrication is blocking.** Suspected invented evidence (fake citation, made-up statistic) is always a `revise` until sourced or removed; never pass it as fact.
- **Every revise finding is actionable** — failed condition + location + concrete fix. No vague notes.

**Preferences (override-able):**

- Order findings by severity — blocking gaps first, then minor ones.
- Reference the condition number/name in each finding so the author maps it back to the bar.
- Keep approve-notes few and clearly non-blocking.

## Gotchas

- **Approving for completeness instead of plannability.** Every section can be present and the PRD still un-plannable (metrics with no targets, abstract features). Judge whether the *build can be planned*, not whether the *template is filled*.
- **False-revise on a thin project.** A small project's PRD is correctly short; collapsed sections it doesn't need are not gaps. Manufacturing a gap from brevity is the most common reviewer error here — calibrate to the project's size.
- **Trusting confident-looking numbers.** A precise statistic with no traceable source is the signature of fabricated evidence, not rigor. Plausibility is not verification — flag the unsourced figure.
- **Drifting the bar.** Reviewing against your personal preferences instead of the eight conditions silently raises the bar above what the author produced to, causing avoidable revise loops. Stick to the shared checklist.
- **Confusing this with engineering design-review.** A PRD is judged for product plannability, not for code-consistency or architecture. Don't apply (or defer to) a spec/ADR/RFC gate on the PRD.
- **Verdict token drift.** "Approved", "LGTM", "needs work", or a verdict buried mid-paragraph will not parse. Emit the literal `VERDICT: approve|revise` on its own line.

## Anti-patterns

- **Rubber-stamp approve.** Skimming and approving to avoid a revise loop — the gate exists to catch un-plannable PRDs; a fabricated metric waved through poisons the whole downstream plan.
- **Nit-pick revise.** Blocking on wording, formatting, or nice-to-haves dressed up as gaps. Revise is for real plannability blockers only.
- **Silent rewrite.** "It was easier to just fix it" — authoring inside a review collapses the produce/judge separation and removes the author's chance to learn the gap.
- **Inventing conditions.** "It should also have a competitive analysis / GTM section" when that isn't in the bar — adding private requirements drifts the review-bar off the produce-bar.
- **Hedged verdict.** "Mostly approve but…" or two verdict lines. Exactly one decision, exactly one token.

## Output

A single review result for one PRD:

- **One verdict line** — `VERDICT: approve` or `VERDICT: revise`, verbatim, on its own line.
- **Findings** — on `revise`, one actionable finding per blocking gap (failed condition + location + concrete fix); on `approve`, optional non-blocking notes.

The abstract consumer is whatever orchestrates the produce→review loop: `approve` accepts the PRD for the next phase (planning); `revise` returns the findings to the producer for a bounded revision pass.

## Related

- A **PRD-authoring** skill — the produce half of the pair; it writes the PRD to the same plannability bar this skill judges against. Pairing them single-sources the bar so produce and review do not drift.
- A **design-review** skill — the sibling gate for engineering design documents (specs, plans, ADRs, RFCs). Distinct gate, distinct bar; not used for the PRD.
- A **PRD template / content-template** tool — owns the section *structure*; this skill judges *quality against the bar*, not structural conformance.

## Progressive disclosure

- `references/plannability-bar.md` — the eight checklist conditions expanded with per-condition pass/gap signals and worked finding examples. Load when a borderline condition needs a sharper pass/gap call.
- `references/sources.md` — research provenance for the review method and fabrication-detection guidance.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap). Claude truncates the combined `description` + `when_to_use` at 1,536 chars in the listing.
- Body ≤ ~500 lines / 5,000 tokens — kept in context every turn.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k tokens, error >50k.
