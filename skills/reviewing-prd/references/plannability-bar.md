# The plannability bar — expanded review conditions

Load this when a borderline PRD needs a sharper pass/gap call on a specific condition. Each condition gives the **pass signal**, the **gap signal**, and a **finding example**. The bar is single-sourced with the PRD-authoring side: the author produces to exactly these conditions, so judging against anything stricter drifts the review-bar off the produce-bar.

The whole bar answers one question: **can the downstream build be planned from this PRD?** A condition fails only on a real, named deficiency — never on style preference. The bar is proportional: a thin project's short PRD passes if every *applicable* condition is met.

---

## 1. Problem evidenced, not asserted

- **Pass:** the problem names who has the pain, what it costs today, and backs it with evidence — qualitative (interviews, support tickets, feedback) and/or quantitative (conversion, churn, drop-off), sized concretely.
- **Gap:** bare assertion ("users want this", "this is a big problem") with no source, no magnitude, no named sufferer; or evidence gestured at but unsourced.
- **Finding:** `revise — Problem (cond. 1): the pain is asserted, not evidenced — no data or who-is-affected. Fix: cite the signal and size it, e.g. "X% of <persona> abandon at <step>, per <source>."`

## 2. Users/personas concrete

- **Pass:** at least the primary persona(s) with real needs and scenarios; user stories ("As a … I want … so that …").
- **Gap:** a generic "the user" with no needs/scenarios a planner could design against.
- **Finding:** `revise — Users (cond. 2): only a generic "user" is named. Fix: define the primary persona's needs + one concrete scenario.`

## 3. Measurable success metrics

- **Pass:** up to ~4 outcome metrics (one can suffice for a thin project), each with a **target value** and a **measurement method** (how it is instrumented/tracked), tied to user value and/or business impact. A single good metric on a thin PRD is not a gap.
- **Gap:** a metric with no target; no way to measure it; a vanity metric (impressions, raw signups) untied to outcome; or a metric *dump* (many unprioritized KPIs). Targetless or unmeasurable = gap.
- **Finding:** `revise — Metrics (cond. 3): "improve engagement" has no target or measurement method. Fix: e.g. "D7 retention ≥ 40%, measured via the retention cohort event."`

## 4. Defensible MVP boundary

- **Pass:** explicit in-scope vs out-of-scope split; named **non-goals**; **release criteria** (definition of done for first launch).
- **Gap:** fuzzy/everything-in-v1 scope; no non-goals (without an out-of-scope list, everything is in scope — the scope firewall is missing); no stated "ready to ship" bar.
- **Finding:** `revise — Scope (cond. 4): no non-goals or release criteria. Fix: list what's explicitly out for v1 and the bar that defines done.`

## 5. Concrete, plannable features

- **Pass:** a feature set + **acceptance criteria** specific enough to derive milestones/tasks; criteria independently testable with clear pass/fail (Given/When/Then is a strong sign), so engineers can estimate and sequence.
- **Gap:** features are abstract goals with no testable "done"; a planner cannot estimate or break them into tasks.
- **Finding:** `revise — Features (cond. 5): "support notifications" has no acceptance criteria. Fix: add testable criteria, e.g. "Given <state>, When <action>, Then <observable result>."`

## 6. No fabricated evidence

- **Pass:** every citation, statistic, and research figure is real and verifiable, or is honestly flagged as an assumption to validate.
- **Gap:** precise-but-unsourced numbers; named studies that can't be traced; suspiciously round/confident figures. AI-authored PRDs fabricate plausible citations and data at a high rate, so plausibility is **not** verification. This gap is serious — never let it pass as fact.
- **Finding:** `revise — Evidence (cond. 6): "73% of users churn here" cites no source and reads as fabricated. Fix: provide a verifiable source, or restate as an explicit assumption to validate before build.`

## 7. Open questions + risks surfaced

- **Pass:** genuine unknowns and risks stated openly — risks with likelihood/impact + mitigation; open questions listed, not hidden.
- **Gap:** the PRD reads as falsely complete — obvious unknowns absent, or an assumption presented as settled fact.
- **Finding:** `revise — Risks/OQs (cond. 7): no open questions despite obvious unknowns (e.g. <X>). Fix: surface the real unknowns and any risks with mitigations.`

## 8. Clear and unambiguous

- **Pass:** jargon-free, consistent terminology; each requirement reads one way to a cross-functional audience.
- **Gap:** ambiguity that would make two planners build two different things.
- **Finding:** `revise — Clarity (cond. 8): "fast" and "real-time" are used interchangeably and undefined. Fix: define each term once and use it consistently (state the latency target).`
- *(Non-collapsing baseline — clarity applies at any project size.)*

## 9. Non-functional requirements carry targets

- **Pass:** the *load-bearing* NFR categories for the archetype are present, each with a **numeric/checkable target** — performance (p95 latency/throughput), availability/reliability (an SLO), security, privacy/data-handling, accessibility (WCAG 2.2 AA floor), scalability, maintainability, compatibility, i18n, compliance — proportional to the archetype.
- **Gap:** a load-bearing NFR stated as a vague adjective ("should be fast/secure/scalable") with no target.
- **Collapse (proportional):** a thin internal tool needs few categories; a deliberately best-effort NFR, *stated as such*, is not a gap. Don't demand SLOs a trivial tool doesn't need.
- **Finding:** `revise — NFRs (cond. 9): the API PRD says "must be performant" with no target. Fix: state a numeric target, e.g. "p95 < 300ms over a rolling 30-day window."`

## 10. Traceable (no orphans)

- **How to check (structural):** cross-reference the Goals section against the Requirements/Features section — no traceability matrix is required for the check. Confirm every feature serves ≥1 stated goal, every goal has ≥1 feature, metrics tie to goals, stories have AC.
- **Pass:** the chain holds — no orphan feature, no goal without a feature.
- **Gap:** a feature serves no stated goal (gold-plating a planner can't justify), or a goal has zero features (an unmet goal).
- **Collapse / baseline:** a tiny PRD with one goal/one feature traces trivially (no elaborate matrix needed) — but the *no-orphan rule itself is a non-collapsing baseline*: a feature serving no goal is broken at any size.
- **Finding:** `revise — Traceability (cond. 10): feature "bulk export" maps to no stated goal. Fix: tie it to a goal, or move it to non-goals.`

## 11. Dependencies named

- **Pass:** cross-team and external dependencies (services, data, third parties, required sign-offs) that gate sequencing are surfaced (a standalone tool may state "none").
- **Gap:** a hard dependency that blocks sequencing is buried in prose or absent.
- **Collapse (proportional):** a self-contained tool with no external dependencies trivially holds.
- **Finding:** `revise — Dependencies (cond. 11): the PRD relies on a new auth service but never names it as a dependency. Fix: list it under Dependencies with its owner + status.`

## 12. Amend integrity (delta-scoped — only when reviewing an amendment)

- **Scope:** review the **change + its ripple**, NOT a full re-review of the unchanged PRD.
- **Pass:** (a) the delta meets the plannability bar on what it touched; (b) change history present (who/when/what/why); (c) superseded content marked, not silently dropped; (d) ripple integrity — no dangling downstream trace.
- **Gap:** a changelog-less amend; a silently-deleted requirement; a dropped feature leaving its metric/AC orphaned; a delta that fails the bar on the section it changed.
- **Collapse:** a greenfield first build does not exercise this; do NOT false-revise a small, clean, traceable delta for not re-justifying untouched sections.
- **Finding:** `revise — Amend (cond. 12): the metric for the removed "guest checkout" feature still references it. Fix: remove/supersede the orphaned metric and note it in the changelog.`

---

## Calibration notes

- **Approve a thin-but-complete PRD.** Proportionality is part of the bar. A small project legitimately collapses sections; collapsed-because-not-needed is not a gap. Manufacturing a gap from brevity is the most common false-revise.
- **One real gap is enough to revise; zero gaps means approve.** Don't tally nice-to-haves; don't approve over a true blocker to be agreeable.
- **Fabrication outranks everything.** A single fabricated statistic is a `revise` even if all eleven other conditions pass — a poisoned input corrupts the downstream plan.
- **Conditions 9–12 collapse on a thin PRD.** NFR targets, traceability matrices, dependency lists, and amend-review apply proportionally; the only non-collapsing baselines are fabrication (6), the no-orphan rule (10), and clarity (8). Don't false-revise a thin PRD for an inapplicable new condition.
