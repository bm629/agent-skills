---
name: reviewing-prd
description: >
  Use when reviewing or judging a finished PRD (product requirements document) to
  decide whether the downstream build can be planned from it — an acceptance gate,
  not authoring. Judges the PRD against a 12-condition plannability bar: the problem
  is evidenced (not asserted), users are concrete, success metrics are measurable
  (with guardrails where gameable), the MVP boundary is defensible, features +
  acceptance criteria are concrete, non-functional requirements carry numeric targets,
  the problem→goal→metric→feature→AC chain is traceable (no orphans), dependencies
  are named, no evidence is fabricated, and open questions are surfaced. Also reviews
  an AMEND as a delta-scoped review. Emits exactly `VERDICT: approve|revise` plus
  actionable findings. Approves a PRD that meets the bar (no false-revise on a thin
  one) and revises only on a real, named gap. Not for authoring or fixing a PRD, not
  for engineering design docs (specs, ADRs, RFCs), and not for other document types.
extensions:
  claude:
    when_to_use: "judging a finished or amended PRD against the 12-condition plannability bar and emitting an approve/revise verdict"
    argument-hint: "<the finished PRD to review (or the amended PRD + its changelog)>"
version: "1.2.0"
forge:
  status: unreviewed
  forged: 2026-06-04
  reviewed: null
---

# `reviewing-prd` — SKILL.md

> **Variant:** standard · **When to use:** judging a finished (or amended) PRD as an acceptance gate — checking it is plannable, then emitting `VERDICT: approve|revise` with actionable findings.

## Overview

This skill is the *review* half of a producing/judging PRD pair. Loaded by a reviewer who has a **finished PRD** in hand, it judges that PRD against one question: **can the downstream build be planned from it?** It applies a fixed **12-condition plannability checklist** — the same bar `authoring-prd` produces to, so the produce-bar and review-bar do not drift — detects fabricated evidence, then emits a single machine-parseable verdict plus findings the author can act on in one revision pass. It is an acceptance gate — it does **not** author, fix, or rewrite the PRD; it judges and returns findings, and the producer revises.

## When to activate

- A finished PRD needs an accept/revise decision before downstream planning begins.
- You are the independent reviewer / gate for a PRD a producer just authored.
- Re-judging a revised PRD after a prior `revise` verdict.
- Judging an **amended** PRD (a versioned delta) — apply the delta-scoped review (cond-12).

**Do NOT activate when:**

- Authoring or repairing a PRD → use `authoring-prd`. This skill never writes the PRD.
- Reviewing an engineering design document — a feature-spec, technical-design, plan, ADR, or RFC → use a `design-review` skill. That gate verifies engineering claims against the codebase; **this** gate judges product plannability and is **not** used for the PRD's engineering *downstream* siblings.
- Checking template/section conformance → that is a template concern. This skill judges *quality against the bar*, not whether every heading is present.
- Reviewing any other document type.

## Workflow

### Step 1: Read the whole PRD with fresh, independent eyes

Read the PRD end to end as if encountering it for the first time, without the author's framing. Your stance is a gatekeeper for the *next* step (planning): findings carry weight only when they show the build cannot be planned as written. Note where a claim, metric, scope line, or dependency is load-bearing — those are the spots Step 2 scrutinizes. If this is an amend, also read the change-log / version delta (cond-12).

### Step 2: Run the 12-condition plannability checklist — judge each condition

For each condition that **applies**, decide **pass** or **gap**. A condition fails only on a *real, named* deficiency — "I'd have phrased it differently" is not a gap. For each gap, capture the exact location and what is missing (Step 4 turns it into an actionable finding). Conditions 9–12 are new in v1.2.0; each carries a **proportionality collapse** so a thin PRD is never newly failed (cond-10's no-orphan core stays a non-collapsing baseline — only its matrix collapses on a thin PRD).

1. **Problem evidenced, not asserted.** Backed by evidence — qualitative (interviews, tickets, feedback) and/or quantitative (conversion, churn, drop-off) — sized concretely (e.g. "drop-off at step 3 affects 42% of new accounts"), and framed as a real user job. *Gap* when the problem is a bare assertion or evidence is vague with no source, magnitude, or who-is-affected.
2. **Users/personas concrete.** At least the primary persona(s) with real needs and scenarios (user stories). *Gap* when users are a generic "the user" with no needs/scenarios a planner could design against.
3. **Measurable success metrics (+ guardrails).** Up to ~4 outcome metrics (one can suffice for a thin project), **each** with a **target** and a **measurement method**. *Gap* when a metric has no target, no measurement, or is a vanity metric; a metric-dump (ten unprioritized KPIs) is a gap. **Guardrail check:** flag a missing guardrail/counter-metric **only** when a headline metric is *obviously* gameable in a way that harms a *stated* goal (not a speculative "could be gamed"). Do **not** revise a thin PRD for a single good metric.
4. **Defensible MVP boundary.** Explicit in-scope vs out-of-scope split, named **non-goals**, and **release criteria**. *Gap* when scope is everything-in-v1, non-goals are absent, or there is no "ready to ship" bar.
5. **Concrete, plannable features.** A feature set + **acceptance criteria** specific enough to derive milestones/tasks, independently testable (Given/When/Then is a strong sign). *Gap* when features are abstract goals with no testable "done."
6. **No fabricated evidence.** Every citation/statistic/figure is real and verifiable, **or** honestly flagged as an assumption to validate. Treat precise-but-unsourced numbers and untraceable studies as suspect — AI-authored PRDs fabricate plausible citations/data at a high rate. *Gap* (serious) when evidence appears invented and is presented as fact. An honestly-labelled assumption is **not** a gap. **Never let a fabricated number pass as fact.** (Non-collapsing baseline — applies at any size.)
7. **Risks, dependencies-context, open questions surfaced.** Genuine unknowns and risks stated openly (risks with likelihood/impact + mitigation; open questions listed), not buried. *Gap* when the PRD reads as falsely complete. (Dependency *completeness* is cond-11; this condition is about surfacing risk/unknowns honestly.)
8. **Clear and unambiguous.** Jargon-free, consistent terminology (one name per entity), so a cross-functional reader interprets each requirement one way. *Gap* when ambiguity would make two planners build two different things. (Non-collapsing baseline.)
9. **Non-functional requirements carry targets.** The *load-bearing* NFR categories for the archetype are present, each with a **numeric/checkable target** (performance/SLO/security/privacy/accessibility WCAG 2.2 AA/scalability/compliance as applicable). *Gap* when a load-bearing NFR is a vague adjective ("should be fast/secure") with no target. **Collapse:** a thin internal tool needs few categories; a deliberately best-effort NFR, *stated as such*, is not a gap — do not demand SLOs a trivial tool doesn't need.
10. **Traceable (no orphans).** Checked **structurally** by cross-referencing the Goals section against the Requirements/Features section: every feature serves ≥1 stated goal, and every goal has ≥1 feature; metrics tie to goals; stories have AC. *Gap* when a feature serves no stated goal, or a goal has zero features. **Collapse:** a tiny PRD with one goal/one feature traces trivially. (Non-collapsing baseline for the no-orphan rule — a feature serving no goal is broken at any size; the collapse is only that small PRDs need no elaborate matrix.)
11. **Dependencies named.** Cross-team and external dependencies (services, data, third parties, required sign-offs) that gate sequencing are surfaced. *Gap* when a hard dependency that blocks sequencing is buried in prose or absent. **Collapse:** a standalone tool with no external dependencies trivially holds ("none" is a valid answer).
12. **Amend integrity (delta-scoped — only when reviewing an amendment).** Review the **change + its ripple**, NOT a full re-review of the unchanged PRD: (a) the delta meets the plannability bar on what it touched; (b) change history present (who/when/what/why); (c) superseded content marked, not silently dropped; (d) ripple integrity — no dangling downstream trace (a dropped feature leaving its metric/AC orphaned). **Collapse:** a greenfield first build does not exercise this; a clean, well-scoped, traceable delta is an `approve` — do not false-revise a small amend for failing to re-justify untouched sections.

**Authoring aids are judged by outcome, not presence.** Metric/prioritization frameworks (North Star/OKR/HEART/AARRR; RICE/MoSCoW/Kano), archetype-specific overlays, GTM/launch/support readiness, opportunity sizing, pre-mortem, and JTBD notation are author *aids* — judge the OUTCOME (right metrics chosen, defensible boundary, archetype-appropriate completeness), **never** require a named framework or a specific section. Demanding a GTM section, a RICE score, or an "ML section" that the bar does not list is an invented-condition error (see anti-patterns).

**Proportionality.** "Concrete enough to plan from" scales with the project. A thin project legitimately collapses sections it does not need — a small, complete PRD that satisfies every *applicable* condition **passes**. Judge completeness-of-decisions, not word count. Do not manufacture a gap from brevity or from an omitted-but-inapplicable section (the richer template has more optional sections — judge the bar, not template-section presence).

### Step 3: Decide the verdict

- **approve** — every applicable condition passes. The build can be planned from this PRD as written. Approve even if you can imagine stylistic improvements; the bar is plannability, not perfection.
- **revise** — one or more applicable conditions have a real, named gap that blocks planning (a metric with no target, no non-goals, an abstract feature, a fabricated statistic, a vague load-bearing NFR, an orphan feature, a buried hard dependency, a changelog-less amend, etc.).

Do not revise to signal effort or to request nice-to-haves. A condition is either met or it isn't.

### Step 4: Emit the verdict + actionable findings

Emit the verdict as a single line — the literal text `VERDICT: approve` or `VERDICT: revise`, on its own line, with **no** surrounding code fences, quotes, or extra words (the fences here are illustration only):

```
VERDICT: approve
```

Then, on the following lines, list findings. On `revise`, every finding is **actionable** — the failed condition (by number/name), the exact location, and **how to fix it** — so the author can resolve it in one pass. On `approve`, findings are optional non-blocking notes; do not let them imply a revision is required.

A good finding names the gap and the fix:

> **revise** — NFRs (cond. 9): the API PRD lists "must be fast" with no target. Fix: state a numeric target, e.g. "p95 < 300ms over a rolling 30-day window."
> **revise** — Traceability (cond. 10): feature "bulk export" maps to no stated goal. Fix: tie it to a goal or move it to non-goals.

A bad finding is vague and unactionable:

> The requirements section could be stronger. *(Which requirement? Why does it fail? What fixes it?)*

## Rules

**Hard rules (never violate):**

- **Emit exactly one verdict line, `VERDICT: approve` or `VERDICT: revise`** — that literal token, on its own line, nothing else on it. Downstream tooling parses it.
- **Judge, never author.** Return findings; do not rewrite, fix, or fill in the PRD. The producer revises.
- **Single-sourced bar.** Judge against the 12 conditions in Step 2 — the same bar the author produces to. Do not invent extra conditions or a stricter private standard.
- **No invented conditions.** Author aids (frameworks, archetype overlays, GTM, opportunity sizing, pre-mortem) are judged by outcome, never required by name. "It should also have a GTM/competitive/ML section" or "it should use RICE" — when that isn't a listed condition — drifts the review-bar off the produce-bar. Forbidden.
- **No false-revise.** A PRD that meets every applicable condition is approved, even a thin one (conditions 9–12 collapse on a thin PRD). Revise only on a real, named gap.
- **No false-approve.** Never approve over a genuine gap to be agreeable.
- **Fabrication is blocking.** Suspected invented evidence is always a `revise` until sourced or removed; never pass it as fact.
- **Judge against the upstreams the document was given.** Assess against its `depends_on` set. A **not-produced** upstream is **never** a revise trigger; a document that **ignored a produced upstream** it should have drawn on **is** a fair finding.
- **Amend = delta-scoped.** When reviewing an amendment, review the change + ripple (cond-12), not the whole unchanged PRD.
- **Every revise finding is actionable** — failed condition + location + concrete fix.

**Preferences (override-able):**

- Order findings by severity — blocking gaps first, then minor ones.
- Reference the condition number/name in each finding so the author maps it back to the bar.
- Keep approve-notes few and clearly non-blocking.

## Gotchas

- **Approving for completeness instead of plannability.** Every section can be present and the PRD still un-plannable (metrics with no targets, abstract features, vague NFRs). Judge whether the *build can be planned*, not whether the *template is filled*.
- **False-revise on a thin project.** A small project's PRD is correctly short; collapsed/omitted inapplicable sections (no NFR matrix, no dependencies, no changelog) are not gaps. Manufacturing a gap from brevity — or from the richer template's optional sections being empty — is the most common reviewer error.
- **Inventing conditions.** Demanding a GTM/competitive/ML section or a specific framework the bar doesn't list — adding private requirements drifts the review-bar. Judge the outcome, not the artifact's table of contents.
- **Speculative guardrail demands.** Flagging "this metric could theoretically be gamed" when nothing in the PRD's stated goals is at risk. Cond-3's guardrail check fires only for an *obviously* gameable metric that harms a *stated* goal.
- **Trusting confident-looking numbers.** A precise statistic with no traceable source is the signature of fabricated evidence, not rigor.
- **Re-reviewing the whole PRD on an amend.** Cond-12 is delta-scoped; do not revise untouched, already-approved sections.
- **Confusing this with engineering design-review.** A PRD is judged for product plannability, not code-consistency. Don't apply (or defer to) a feature-spec/ADR/RFC gate on the PRD.
- **Verdict token drift.** "Approved", "LGTM", "needs work", or a verdict buried mid-paragraph will not parse. Emit the literal `VERDICT: approve|revise` on its own line.

## Anti-patterns

- **Rubber-stamp approve.** Skimming and approving — a fabricated metric or an orphan feature waved through poisons the downstream plan.
- **Nit-pick revise.** Blocking on wording, formatting, or nice-to-haves dressed up as gaps.
- **Silent rewrite.** "It was easier to just fix it" — authoring inside a review collapses the produce/judge separation.
- **Inventing conditions.** "It should also have a competitive analysis / GTM section" / "it should use RICE" when that isn't in the 12-condition bar.
- **Over-strict on NFR/traceability for a thin PRD.** Demanding SLOs from a trivial internal tool, or a traceability matrix from a one-goal PRD — the conditions collapse proportionally.
- **Hedged verdict.** "Mostly approve but…" or two verdict lines. Exactly one decision, exactly one token.

## Output

A single review result for one PRD:

- **One verdict line** — `VERDICT: approve` or `VERDICT: revise`, verbatim, on its own line.
- **Findings** — on `revise`, one actionable finding per blocking gap (failed condition + location + concrete fix); on `approve`, optional non-blocking notes.

The abstract consumer is whatever orchestrates the produce→review loop: `approve` accepts the PRD for the next phase (planning); `revise` returns the findings to the producer for a bounded revision pass.

## Related

- **`authoring-prd`** — the produce half of the pair; it writes the PRD to the same 12-condition plannability bar this skill judges against. Pairing them single-sources the bar so produce and review do not drift.
- A **`design-review`** skill — the sibling gate for engineering design documents (feature-spec, technical-design, plans, ADRs, RFCs). Distinct gate, distinct bar; not used for the PRD.
- A **PRD template / content-template** tool — owns the section *structure*; this skill judges *quality against the bar*, not structural conformance.

## Progressive disclosure

- `references/plannability-bar.md` — the 12 checklist conditions expanded with per-condition pass/gap signals and worked finding examples (incl. the structural traceability check, the gameability bar, the NFR load-bearing scoping, and the delta-scoped amend review). Load when a borderline condition needs a sharper pass/gap call.
- `references/sources.md` — research provenance for the review method and fabrication-detection guidance.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap). Claude truncates the combined `description` + `when_to_use` at 1,536 chars in the listing.
- Body ≤ ~500 lines / 5,000 tokens — kept in context every turn.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k tokens, error >50k.
