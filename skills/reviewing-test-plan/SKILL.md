---
name: reviewing-test-plan
description: >
  Use when reviewing/judging a test plan / QA verification plan — deciding
  whether a tester can execute it and every behavior is covered. A gate, not
  authoring. Judges it against a single-sourced 10-condition bar: every handed-in
  upstream behavior (feature-spec/api-spec ops+errors, else PRD) has >=1
  TRACEABLE case; functional levels fit; entry/exit testable (coverage floor +
  open-defect threshold); environments + test data specified; each case has
  preconditions + steps + observable result (a metric-threshold-on-a-dataset for
  ML) + traces-to; the catalog is RISK-WEIGHTED (coverage gap, padded/thin, OR
  combinatorial blow-up = a finding); each warranted non-functional type
  (perf/security/WCAG 2.2 AA/compat/i18n) carries a target; an amend is reviewed
  delta-scoped; nothing fabricated. Emits exactly `VERDICT: approve|revise` +
  actionable findings; approves a proportionally-sized plan, revises only on a
  named gap. Not for authoring it, the release runbook, design-review, or the
  test scripts.
extensions:
  claude:
    when_to_use: "judging a finished QA / verification test plan against the 10-condition coverage + testability bar (every upstream behavior traceable; risk-weighted not combinatorial; warranted non-functional targets; delta-scoped amend; nothing fabricated) and emitting an approve/revise verdict"
    argument-hint: "<the finished test plan to review, plus the handed-in upstreams (feature-spec / api-spec / PRD); for an amend, the change request too>"
version: "1.1.0"
forge:
  status: reviewed
  forged: 2026-06-05
  reviewed: 2026-06-15
---

# `reviewing-test-plan` — SKILL.md

> **Variant:** standard · **When to use:** judging a finished (or amended) QA/verification test plan as an acceptance gate — checking a tester can execute it, every upstream behavior has a traceable case, the catalog is risk-weighted not combinatorial, and the warranted non-functional testing carries numeric targets, then emitting `VERDICT: approve|revise` with actionable findings.

## Overview

This skill is the *review* half of an authoring/judging test-plan pair. Loaded by a reviewer who holds a **finished QA/verification test plan** — the document stating what to test, at what level, in what environment, with what data, to what done-criteria, plus the case catalog to run — it judges that document against one question: **can a tester execute this plan with no questions, does every behavior in the handed-in upstreams have at least one traceable test case, and is the catalog sized by risk (not the full input-permutation cross-product, not skeletal)?** It applies a fixed **10-condition coverage + testability checklist** — the same bar a test-plan author produces to (`authoring-test-plan` Step-7), so the produce-bar and the review-bar do not drift — then emits a single machine-parseable verdict plus findings the author can act on in one revision pass. It is an acceptance gate: it does **not** author, fix, or rewrite the plan; it judges and returns findings, and the producer revises.

The **single most load-bearing checks** are **coverage completeness** (enumerate every upstream behavior/operation/error and confirm each has >=1 traceable case — a behavior with no case is the highest-impact defect) and **catalog sizing** (risk-weighted, not a combinatorial blow-up and not thin/padded). Both are easy to miss when the plan *looks* thorough.

## When to activate

- A finished QA/verification test plan needs an accept/revise decision before testing begins or before it feeds a release runbook's exit criteria.
- You are the independent reviewer / gate for a test plan a producer just authored, and you have the upstreams (feature-spec / api-spec / PRD) to check coverage against.
- Re-judging a revised test plan after a prior `revise` verdict, or reviewing an **amend** (a change request handed in against an approved plan — judge it delta-scoped, cond. 10).

**Do NOT activate when:**

- Authoring or repairing a test plan -> use `authoring-test-plan` (it produces to the same bar this skill asserts). This skill never writes the document.
- Reviewing the **release/deployment runbook** — the go-to-production procedure (deploy steps, verification, rollback) -> use a release-runbook-review skill. The runbook *reuses* this plan's exit criteria; the bars differ (executability/rollback vs coverage/testability).
- Reviewing **engineering design documents** — a spec, plan, design doc, RFC, or ADR -> use a design-review skill that verifies design claims against the codebase. That gates the design; this gates the verification plan derived downstream of it.
- Judging or running the **executable test scripts** (pytest / Playwright / etc.) — those are implementation, downstream of this plan. This gate judges the plan *document*, not the automation code or a test run's results.
- Checking template/section conformance -> that is a template concern. This skill judges *quality against the bar*, not whether every heading is present.

## Workflow

### Step 1: Read the whole plan with fresh eyes — and pull up the upstreams

Read the test plan end to end as if you were the tester who must execute it tomorrow, without the author's framing. Your stance is a gatekeeper for that tester: a finding carries weight only when it shows the tester **cannot execute a case, cannot decide whether done-criteria are met, or finds a behavior with no case**. Identify the **project archetype** the plan is sized to (a thin CLI vs a broad UI product) — Step 2's proportionality calibration depends on it. Critically, **load the handed-in upstreams** (feature-spec / api-spec / PRD / NFRs — whatever the project actually produced): they are your **coverage checklist**. Enumerate every behavior / acceptance criterion (feature-spec), every operation + error case (api-spec), or — if those weren't produced — every requirement (PRD); note the NFRs that warrant non-functional testing. Never assume a fixed input; enumerate from **whatever upstream was handed in**. If an upstream was **not** handed in, record that now — flag it as an assumption in Step 4 and judge coverage on what you have; never invent an expectation of a document the project didn't produce, and never default to approve because the checklist couldn't be fully run. If a **change request** was handed in against an existing plan, this is an **amend** — run cond. 10 delta-scoped (Step 2).

### Step 2: Run the coverage + testability checklist — judge each condition

For each condition below, decide **pass** or **gap**. A condition fails only on a *real, named* deficiency — "I'd have ordered the cases differently" is not a gap. For each gap, capture the exact location and what is missing (Step 4 turns it into an actionable finding). These ten conditions are the **single-sourced bar** (the same conditions `authoring-test-plan` Step-7 produces to); do not add private ones. Depth + worked pass/gap signals: `references/coverage-testability-bar.md`.

1. **Complete coverage.** Every behavior / acceptance criterion in the handed-in feature-spec, and every operation + error case in the handed-in api-spec (else every requirement in the PRD), has **>=1 traceable test case**. *Gap* when an enumerated upstream behavior/operation/error has **no** case pointing back to it — the highest-impact defect class. (Binds at any size.)
2. **Appropriate functional levels.** The functional levels & types chosen fit the project — unit/integration/e2e/acceptance present as the system warrants; regression/smoke as warranted; any omission justified, not silent. *Gap* when a level the system clearly warrants is absent with no rationale (e.g. no integration cases for a multi-service system). *(Non-functional testing is cond. 9, not here.)* Proportionality: a thin project collapses the levels it doesn't need.
3. **Testable entry/exit criteria.** Entry and exit ("done") criteria are observable/measurable — a reader can **mechanically** decide each (e.g. "all High-priority cases pass; every behavior has a passing traceable case; no open Critical/High defect"). The exit ties to a **coverage floor + an open-defect threshold**; coverage phrased against requirements/risk, not a bare code-coverage %. *Gap* when a criterion is vague ("testing looks good") so two readers could disagree. Proportionality: a thin plan has a short criteria list, still decidable.
4. **Environments + test data specified.** Each level states **where** it runs and the **data/fixtures** it needs + how they're provisioned/reset + how sensitive data (PII/PHI) is handled. *Gap* when a level names no environment, or cases assume fixtures the plan never specifies. Proportionality: a thin plan = one env, simple fixtures.
5. **Each catalog case is executable + traceable.** Every case has **preconditions**, **single-action steps**, an **observable expected result** (the exact message/error for negatives; for an ML/probabilistic case a **metric-threshold on a named dataset** or a metamorphic relation — "the model is accurate"/"results are relevant" is the un-runnable result this rejects), and a **traces-to**. *Gap* when a case lacks preconditions, has vague/multi-action steps, has a non-observable expected result, or has no traces-to. (Binds at any size — the executability floor.)
6. **Risk-prioritized + risk-weighted.** The plan prioritizes by **Likelihood x Impact**, and catalog **depth follows risk** — more cases (boundaries, equivalence partitions, decision-table/state-transition/pairwise selections, negative paths) on high-risk areas, fewer on trivial ones — **NOT** the full input-permutation cross-product. *Gap* in three directions: a **coverage gap** (too few cases for the risk), a **combinatorial blow-up** (every permutation — e.g. all 1,024 combinations of a 10-switch module instead of risk + pairwise), **or** a **padded/thin catalog** (cases that don't add coverage, or a high-risk area with only a happy-path case). The case-design techniques are author aids — judge the *outcome*, never "draw a decision table".
7. **No fabrication.** Every case traces to a **real** upstream; any coverage gap (an untestable requirement, a missing NFR) is surfaced as an **explicit assumption**, never filled with an **invented** behavior. *Gap* when a case tests a behavior **no upstream declares**. **Spot-check** a sample of cases' traces-to against the actual upstreams. (Binds at any size.)
8. **Proportional to the archetype.** The catalog and the level set are sized to the project — a thin CLI gets a handful of cases and may collapse non-functional testing; a large UI product gets many. *Gap* only when the plan is **skeletal** for its archetype or **combinatorial** (cond. 6). Right-sizing is not a gap.
9. **Non-functional testing (warranted types carry numeric targets).** Each non-functional type the **NFRs / archetype warrant** is present with a checkable approach + a **numeric/standard target**: performance (load profile + p95/throughput), security (a threat-derived set), accessibility (**WCAG 2.2 AA**), usability, compatibility (a matrix), i18n/l10n. *Gap* when a warranted type is present with no approach/target ("we'll test performance" with no profile/target), or an NFR exists with no non-functional testing covering it. **Proportionality (load-bearing):** a thin project with no NFR warrants **none** — its absence is NOT a gap; never demand a non-functional type the archetype doesn't warrant, and never fabricate a target. (This condition owns the non-functional axis; cond. 2 is functional-only — a missing warranted perf level is ONE finding here, not two.)
10. **Delta-scoped amend (only when a change request is handed in).** When the input includes a change request/delta against an existing plan, judge **delta-scoped**: the delta is in-scope + edit-not-redraw; the coverage map was **re-traced** (changed behaviors re-mapped, removed ones retired, no behavior left without a case); the **regression set was selected by impact + risk** (not all, not none); a discovered-defect amend added a **traced regression case**; the plan's **own version + changelog** is present and superseded cases marked; the touched cases still meet conds. 5–6 — **NOT** a full re-review of the unchanged plan. *Gap* when the delta is a silent redraw, leaves a changed behavior without a re-traced case, skips/over-runs regression selection, or lacks the version/changelog. **Proportionality:** on a greenfield first build (no change request) this condition is **n/a** — never a gap.

**Proportionality.** "Can a tester execute it and is every behavior covered" scales with the project. A thin project's plan legitimately **collapses what it doesn't need** — no non-functional testing without an NFR (cond. 9 n/a), no integration tier without seams, a short catalog if there are few behaviors, no amend section greenfield (cond. 10 n/a). That is correct sizing, not a gap. Judge the **tester's ability to execute and the coverage of the enumerated behaviors**, not case count. A small, complete plan that satisfies every *applicable* condition **passes**; do not manufacture a gap from brevity. (Conditions 1, 5, 7 still bind at any size.)

### Step 3: Decide the verdict

- **approve** — every applicable condition passes. A tester can execute the plan as written, every enumerated upstream behavior has a traceable case, the catalog is risk-weighted, the warranted non-functional testing carries targets, and nothing is fabricated. Approve even if you can imagine stylistic improvements; the bar is coverage + testability, not perfection — and not maximalism.
- **revise** — one or more applicable conditions have a real, named gap.

Do not revise to signal effort or to request nice-to-haves. A condition is either met or it isn't.

### Step 4: Emit the verdict + actionable findings

Emit the verdict as a single line — the literal text `VERDICT: approve` or `VERDICT: revise`, on its own line, with **no** surrounding code fences, quotes, or extra words (the fences here are illustration only):

```
VERDICT: approve
```

Then, on the following lines, list findings. On `revise`, every finding is **actionable** — the failed condition, the exact location, and **how to fix it**. On `approve`, findings are optional non-blocking notes; do not let them imply a revision is required.

If an **upstream was not handed in**, state that as an explicit assumption (e.g. "api-spec not provided — operation/error coverage (cond. 1) judged only against the feature-spec") and judge the other conditions on what you have. Do not silently pass over the un-runnable check, and do not default to approve.

Good findings name the gap and the fix:

> **revise** — Complete coverage (cond. 1), feature-spec behavior "user can reset password via email link": no case traces to it. Fix: add a case (happy path + the expired/invalid-link negative) with a traces-to back to this behavior.

> **revise** — Non-functional testing (cond. 9): NFR-PERF requires p95 <= 200ms but the plan's performance row states no load profile or target. Fix: add a load profile (concurrency/duration) + the p95 target + the tool, or flag the NFR as unverifiable.

> **revise** — Delta-scoped amend (cond. 10): the change request alters "checkout applies a coupon" but the catalog wasn't re-traced and no regression set was selected. Fix: re-map the coupon coverage row, add/adjust its case, and select the impact+risk regression set (the cart + pricing cases that depend on coupons).

A bad finding is vague and unactionable:

> The coverage could be more thorough. *(Which behavior? Which case? What fixes it?)*

## Rules

**Hard rules (never violate):**

- **Emit exactly one verdict line, `VERDICT: approve` or `VERDICT: revise`** — that literal token, on its own line, nothing else on it. Downstream tooling parses it. No alternate verdict vocabulary.
- **Judge, never author.** Return findings; do not rewrite, fix, or fill in the plan. The producer revises.
- **Single-sourced bar.** Judge against the ten conditions in Step 2 — the same bar the author produces to (`authoring-test-plan` Step-7). Do not invent extra conditions or apply a stricter private standard.
- **Coverage completeness is load-bearing.** Enumerate every behavior/operation/error from the **handed-in upstreams** and confirm each has >=1 traceable case (cond. 1). Enumerate from whatever upstream was handed in — never assume a fixed input.
- **Risk-weighted, not combinatorial, not thin.** A coverage gap, a full input-permutation cross-product, **and** a padded/thin catalog are each a `revise` (cond. 6). The case-design techniques are author aids judged by outcome — never demand a named technique.
- **Non-functional is targeted + proportional.** A warranted non-functional type with no approach/target is a gap (cond. 9); a non-functional type the archetype doesn't warrant is NOT demanded, and no target is ever fabricated. Cond. 9 owns the non-functional axis; cond. 2 is functional-only — never double-count a missing perf level across both.
- **ML cases use a metric-threshold, not a fixed oracle.** An ML/probabilistic case's expected result is a metric-threshold on a named dataset (or a metamorphic relation); "the model is accurate" is the un-runnable result cond. 5 rejects — recognize the probabilistic case, don't impose a new bar.
- **Amend is reviewed delta-scoped (cond. 10), by input signal.** Run cond. 10 ONLY when a change request is handed in; greenfield -> n/a. Judge the delta + coverage/trace integrity + regression selection, not the unchanged plan.
- **No fabrication.** A case testing a behavior no upstream declares is a defect (cond. 7) — a real gap is flagged as an assumption. Spot-check traces-to against the actual upstreams.
- **No false-revise.** A plan meeting every *applicable* condition is approved, even a thin one. Proportional sizing that still covers every enumerated behavior is not a defect. Revise only on a real, named gap.
- **No false-approve.** Never approve over a genuine gap to be agreeable. A blocking gap is a `revise`.
- **Untestable done-criteria is a gap.** An exit criterion two readers could disagree on fails cond. 3 — done-criteria must be mechanically decidable (a coverage floor + an open-defect threshold).
- **Missing upstream is flagged, not silently passed.** Surface it as an explicit assumption; judge the rest on what you have. Never default to approve.
- **Judge against the upstreams the document was given.** A **not-produced** upstream is **never** a revise trigger. But a plan that **ignored a produced upstream** (a handed-in feature-spec whose behaviors have no cases) **is** a fair finding.
- **Every revise finding is actionable** — failed condition + location + concrete fix. No vague notes.

**Preferences (override-able):**

- Order findings by severity — coverage gaps and fabrication first, then catalog-sizing + non-functional, then amend, then minor ones.
- Reference the condition number/name in each finding so the author maps it back to the bar.
- Keep approve-notes few and clearly non-blocking.

## Gotchas

- **Approving for completeness instead of executability.** Every section can be present and the plan still un-executable (cases with no preconditions, vague steps, an unobservable expected result, no traces-to). Judge whether a tester can *execute and trace it*, not whether the *template is filled*.
- **The behavior with no case.** The plan can look thorough — a long catalog, a coverage matrix — while silently missing a case for one upstream behavior. The only catch is to **enumerate the upstream behaviors and tick each** (cond. 1). A long catalog is not proof of coverage.
- **The combinatorial blow-up that reads as rigor.** A catalog enumerating every permutation looks exhaustive but is unmaintainable and misses risk-weighting — 1,024 cases for a 10-switch module is a defect (cond. 6). Check high-risk areas get *depth* and trivial areas get happy-path-only.
- **The thin/padded catalog.** Cases that restate each other (padding), or a high-risk area with only a happy-path case (thin). Both fail cond. 6 even though the count looks fine. Judge depth against *risk*.
- **The untestable exit criterion.** "Testing complete when coverage is good" can't be mechanically decided (cond. 3). A real exit criterion ties to passing cases + an open-defect threshold.
- **"The model is accurate" as an ML expected result.** A non-deterministic system has no fixed oracle — a deterministic pass/fail is un-runnable (cond. 5). Accept a metric-threshold-on-a-named-dataset or a metamorphic relation; don't invent a new bar beyond cond. 5.
- **Non-functional double-count or maximalism.** Don't flag a missing perf level under both cond. 2 and cond. 9 — cond. 9 owns it. And don't demand a non-functional type a thin project's archetype doesn't warrant (cond. 9 is proportional; no NFR -> n/a).
- **The fabricated case.** A case can test a plausible behavior **no upstream declares** (cond. 7). Spot-check traces-to; a case with no real upstream backing is a defect, not coverage.
- **Amend judged as a full review.** On a change request, judge the delta + coverage/trace integrity + regression selection (cond. 10) — not a fresh full review of the unchanged plan; conversely, don't wave through an amend that didn't re-trace coverage or select a regression set.
- **Systematic over-flagging (false-revise).** A reviewer asked to find problems over-corrects, judging sound plans as defective. Calibrate to the bar: a condition is a gap only on a *named, real* deficiency, not a case order or a level choice you'd have made differently.
- **False-revise on a proportionally-sized plan.** A thin project's plan is correctly small — a handful of cases, no non-functional testing without an NFR, no integration tier without seams. That is right-sizing (conds. 1, 5, 7 still bind).
- **Confusing this with the release-runbook or design-review gate.** This judges the **QA/verification plan**. A release-runbook-review judges the operational procedure that *reuses* this plan's exit criteria; design-review gates engineering design docs against the codebase.
- **Verdict token drift.** "Approved", "LGTM", "needs work", or a verdict buried mid-paragraph will not parse. Emit the literal `VERDICT: approve|revise` on its own line.

## Anti-patterns

- **Rubber-stamp approve.** Skimming the catalog's length and approving — the gate exists to catch plans a tester can't execute or that miss a behavior.
- **Skipping the upstream enumeration.** "The catalog is long, so coverage must be fine" — without enumerating the upstream behaviors and ticking each, you miss the highest-impact defect class (cond. 1).
- **Counting cases instead of weighting by risk.** A bigger catalog is not better. The bar is risk-weighted coverage (cond. 6).
- **Inventing conditions.** Adding a private requirement the bar does not carry ("it should include a traceability-tool export / a specific test-management format / a literal decision table / an exploratory tier"). Judge the ten conditions only — the case-design techniques, exploratory/SBTM, and metamorphic testing are author aids judged by OUTCOME, never demanded. This is the load-bearing guard under the new aids.
- **Maximalism.** Demanding a non-functional type, an integration tier, or a fuller catalog from a thin project that doesn't warrant them (cond. 9 is proportional).
- **Nit-pick revise.** Blocking on case-ordering taste or nice-to-haves dressed up as gaps. Revise is for real coverage/executability blockers only.
- **Silent rewrite.** Authoring inside a review collapses the produce/judge separation.
- **Hedged verdict.** "Mostly approve but…" or two verdict lines. Exactly one decision, exactly one token.

## Output

A single review result for one test plan:

- **One verdict line** — `VERDICT: approve` or `VERDICT: revise`, verbatim, on its own line.
- **Findings** — on `revise`, one actionable finding per blocking gap (failed condition + location + concrete fix); on `approve`, optional non-blocking notes.

The plan under review is **textual** today — strategy prose + a coverage matrix + a non-functional matrix + a test-case catalog (markdown via the local docs backend); the review **method + bar are medium-independent** (a future test-management-tool export changes only the medium). The **abstract consumer** is whatever orchestrates the produce->review loop: `approve` accepts the plan for execution (and lets a release runbook reuse its exit criteria); `revise` returns the findings for a bounded revision pass.

## Related

- **`authoring-test-plan`** — the produce half of the pair; it writes the plan to the same coverage + testability bar this skill judges against (its Step-7 = these ten conditions). Pairing them single-sources the bar so produce and review do not drift.
- The upstream **feature-spec / api-spec / PRD / NFRs** — the documents every case derives from; this gate **enumerates their behaviors/operations/errors and checks each has a traceable case** (cond. 1) and that the NFRs are covered (cond. 9). Gated at their own authoring time, not here.
- A **release-runbook-review** skill — the gate for the operational go-to-production runbook that *reuses* this plan's exit criteria. Distinct doc, distinct bar.
- A **design-review** skill — the gate for engineering design documents (spec, plan, RFC, ADR), which verifies claims against the codebase. Distinct gate, distinct artifact; not the verification plan.
- A **test-plan template / content-template** tool — owns the section *structure*; this skill judges *quality against the bar*, not structural conformance.

## Progressive disclosure

- `references/coverage-testability-bar.md` — per-condition pass/gap signals + worked findings for the ten conditions (esp. the deepened cond. 3/4/5 and the new cond. 9 non-functional + cond. 10 amend), and the no-false-revise / inventing-conditions discipline. Load to apply the bar at depth.
- `references/sources.md` — research provenance for the review method (the single-sourced coverage + testability bar; the ISTQB / ISO-IEC-IEEE 29119 / WCAG 2.2 / OWASP / NIST grounding; the reviewer-overcorrection basis for the no-false-revise discipline). Load only to audit where the guidance came from.

## Body budget

- `description` <= 1,024 chars (agentskills.io cap). Claude truncates the combined `description` + `when_to_use` at 1,536 chars in the listing.
- Body <= ~500 lines / 5,000 tokens — kept in context every turn.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k tokens, error >50k.

## Changelog

- **1.1.0** (2026-06-15) — single-sourced restructure to the 10-condition bar matching `authoring-test-plan` 1.1.0: cond. 2 narrowed to FUNCTIONAL levels; new cond. 9 non-functional testing (warranted types carry numeric targets — perf/security/WCAG 2.2 AA/compat/i18n; subsumes the old cond. 2 non-functional clause, no double-count) and cond. 10 delta-scoped amend; deepened cond. 3 (coverage floor + open-defect threshold), cond. 4 (test-data management), cond. 5 (ML metric-threshold recognition); the case-design techniques + exploratory/SBTM + metamorphic testing held as author aids judged by outcome (inventing-conditions guard reinforced). `VERDICT` contract + input contract unchanged.
- **1.0.0** (2026-06-05) — initial reviewed release.
