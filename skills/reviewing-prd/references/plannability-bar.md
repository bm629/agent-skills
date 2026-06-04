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

*(Condition 8 is the source bar's cross-cutting clarity item promoted to its own numbered check — conditions 1–8 here cover the same plannability bar the author produces to, just with clarity called out explicitly; nothing is added or dropped.)*

- **Pass:** jargon-free, consistent terminology; each requirement reads one way to a cross-functional audience.
- **Gap:** ambiguity that would make two planners build two different things.
- **Finding:** `revise — Clarity (cond. 8): "fast" and "real-time" are used interchangeably and undefined. Fix: define each term once and use it consistently (state the latency target).`

---

## Calibration notes

- **Approve a thin-but-complete PRD.** Proportionality is part of the bar. A small project legitimately collapses sections; collapsed-because-not-needed is not a gap. Manufacturing a gap from brevity is the most common false-revise.
- **One real gap is enough to revise; zero gaps means approve.** Don't tally nice-to-haves; don't approve over a true blocker to be agreeable.
- **Fabrication outranks everything.** A single fabricated statistic is a `revise` even if all seven other conditions pass — a poisoned input corrupts the downstream plan.
