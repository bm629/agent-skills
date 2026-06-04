---
name: reviewing-test-plan
description: >
  Use when reviewing/judging a test plan / QA verification plan — deciding whether
  a tester can execute it and every behavior is covered. A gate, not authoring.
  Judges it against a single-sourced coverage + testability bar: every behavior in
  the handed-in upstreams (feature-spec, api-spec operations + errors, else PRD)
  has >=1 TRACEABLE test case; test levels fit the project; entry/exit criteria are
  testable not vague; environments + test data specified; each catalog case has
  preconditions + steps + expected result + traces-to; the catalog is RISK-WEIGHTED
  (a coverage gap, a padded/thin catalog, OR a combinatorial blow-up is a finding);
  nothing fabricated (each case traces to a real upstream, spot-checked). Emits
  exactly `VERDICT: approve|revise` plus actionable findings; approves a
  proportionally-sized plan meeting the bar, revises only on a named gap. Not for
  authoring it, not the release runbook
  (reviewing-release-runbook), not engineering design docs (design-review), not the
  executable test scripts.
extensions:
  claude:
    when_to_use: "judging a finished QA / verification test plan against the coverage + testability bar (every upstream behavior has a traceable case; risk-weighted not combinatorial; nothing fabricated) and emitting an approve/revise verdict"
    argument-hint: "<the finished test plan to review, plus the handed-in upstreams (feature-spec / api-spec / PRD) to check coverage against>"
version: "1.0.0"
forge:
  status: reviewed
  forged: 2026-06-05
  reviewed: 2026-06-05
---

# `reviewing-test-plan` — SKILL.md

> **Variant:** standard · **When to use:** judging a finished QA/verification test plan as an acceptance gate — checking a tester can execute it, every upstream behavior has a traceable case, and the catalog is risk-weighted not combinatorial, then emitting `VERDICT: approve|revise` with actionable findings.

## Overview

This skill is the *review* half of an authoring/judging test-plan pair. Loaded by a reviewer who holds a **finished QA/verification test plan** — the document stating what to test, at what level, in what environment, to what done-criteria, plus the case catalog to run — it judges that document against one question: **can a tester execute this plan with no questions, does every behavior in the handed-in upstreams have at least one traceable test case, and is the catalog sized by risk (not the full input-permutation cross-product, not skeletal)?** It applies a fixed **coverage + testability checklist** — the same bar a test-plan author produces to, so the produce-bar and the review-bar do not drift — then emits a single machine-parseable verdict plus findings the author can act on in one revision pass. It is an acceptance gate: it does **not** author, fix, or rewrite the plan; it judges and returns findings, and the producer revises.

The **single most load-bearing checks** are **coverage completeness** (enumerate every upstream behavior/operation/error and confirm each has >=1 traceable case — a behavior with no case is the highest-impact defect) and **catalog sizing** (risk-weighted, not a combinatorial blow-up and not thin/padded). Both are easy to miss when the plan *looks* thorough.

## When to activate

- A finished QA/verification test plan needs an accept/revise decision before testing begins or before it feeds a release runbook's exit criteria.
- You are the independent reviewer / gate for a test plan a producer just authored, and you have the upstreams (feature-spec / api-spec / PRD) to check coverage against.
- Re-judging a revised test plan after a prior `revise` verdict.

**Do NOT activate when:**

- Authoring or repairing a test plan -> use a test-plan-authoring skill (it produces to the same bar this skill asserts). This skill never writes the document.
- Reviewing the **release/deployment runbook** — the go-to-production procedure a deploying engineer follows (deploy steps, verification, rollback) -> use a release-runbook-review skill. The runbook *reuses* this plan's exit criteria; the bars differ (executability/rollback vs coverage/testability). This judges the QA plan, not the operational runbook.
- Reviewing **engineering design documents** — a spec, plan, design doc, RFC, or ADR -> use a design-review skill that verifies design claims against the codebase. That gates the design; this gates the verification plan derived downstream of it.
- Judging or running the **executable test scripts** (pytest / Playwright / etc.) — those are implementation, downstream of this plan. This gate judges the plan *document*, not the automation code or a test run's results.
- Checking template/section conformance -> that is a template concern. This skill judges *quality against the bar*, not whether every heading is present.

## Workflow

### Step 1: Read the whole plan with fresh eyes — and pull up the upstreams

Read the test plan end to end as if you were the tester who must execute it tomorrow, without the author's framing. Your stance is a gatekeeper for that tester: a finding carries weight only when it shows the tester **cannot execute a case, cannot decide whether done-criteria are met, or finds a behavior with no case**. Identify the **project archetype** the plan is sized to (a thin CLI vs a broad UI product) — Step 2's proportionality calibration depends on it. Critically, **load the handed-in upstreams** (feature-spec / api-spec / PRD — whatever the project actually produced): they are your **coverage checklist**. Enumerate every behavior / acceptance criterion (feature-spec), every operation + error case (api-spec), or — if those weren't produced — every requirement (PRD). Never assume a fixed input; enumerate from **whatever upstream was handed in**. If an upstream was **not** handed in, record that now — you will flag it as an assumption in Step 4 and judge coverage on what you have; never invent an expectation of a document the project didn't produce, and never default to approve because the checklist couldn't be fully run.

### Step 2: Run the coverage + testability checklist — judge each condition

For each condition below, decide **pass** or **gap**. A condition fails only on a *real, named* deficiency — "I'd have ordered the cases differently" is not a gap. For each gap, capture the exact location and what is missing (Step 4 turns it into an actionable finding). These conditions are the **single-sourced bar** (the shared test-plan dossier — the same conditions a test-plan author produces to); do not add private ones.

1. **Complete coverage.** Every behavior / acceptance criterion in the handed-in feature-spec, and every operation + error case in the handed-in api-spec (else every requirement in the PRD), has **>=1 traceable test case**. *Gap* when an enumerated upstream behavior/operation/error has **no** case pointing back to it — the highest-impact defect class.
2. **Appropriate levels.** The test levels & types chosen fit the project — unit/integration/e2e present as the system warrants; performance/security present **when an NFR exists**; any omission is justified, not silent. *Gap* when a level the system clearly warrants is absent with no rationale (e.g. no integration cases for a multi-service system), or an NFR exists with no non-functional level covering it.
3. **Testable entry/exit criteria.** Entry and exit ("done") criteria are observable/measurable — a reader can **mechanically** decide whether each is met (e.g. "all High-priority cases pass, no open Critical defect, every behavior has a passing traceable case"). *Gap* when a criterion is vague ("testing looks good", "enough coverage") so two readers could disagree on whether it's met.
4. **Environments + test data specified.** Each level states **where** it runs and the **data/fixtures** it needs. *Gap* when a level names no environment, or cases assume fixtures/data the plan never specifies.
5. **Each catalog case is executable + traceable.** Every case has **preconditions**, **single-action steps**, an **observable expected result** (including the exact message/error for negative cases), and a **traces-to** back-reference to an upstream behavior/operation/error. *Gap* when a case is missing preconditions, has vague/multi-action steps, has an expected result that isn't observable, or has no traces-to.
6. **Risk-prioritized + risk-weighted.** The plan prioritizes by **Likelihood x Impact**, and catalog **depth follows risk** — more cases (boundaries, equivalence partitions, negative paths) on high-risk areas, fewer on trivial ones — **NOT** the full input-permutation cross-product. *Gap* in three directions: a **coverage gap** (a behavior with too few cases for its risk), a **combinatorial blow-up** (enumerating every input permutation — e.g. all 1,024 combinations of a 10-switch module instead of risk + pairwise), **or** a **padded/thin catalog** (cases that don't add coverage, or a high-risk area with only a happy-path case).
7. **No fabrication.** Every case traces to a **real** upstream; any coverage gap (an untestable requirement, a missing NFR for a performance level) is surfaced as an **explicit assumption**, never filled with an **invented** behavior to test. *Gap* when a case tests a behavior **no upstream declares** (a fabricated case) instead of the gap being flagged. **Spot-check** a sample of cases' traces-to against the actual upstreams — this is the no-fabrication discipline.
8. **Proportional to the archetype.** The catalog and the level set are sized to the project — a thin CLI gets a handful of cases and may collapse non-functional levels; a large UI product gets many. *Gap* only when the plan is **skeletal** for its archetype (a broad product with a handful of cases) or **combinatorial** (see cond. 6). Right-sizing is not a gap.

**Proportionality.** "Can a tester execute it and is every behavior covered" scales with the project. A thin project's plan legitimately **collapses levels it doesn't need** — no performance level if there's no NFR, no integration tier if there are no seams, a short catalog if there are few behaviors. That is correct sizing, not a gap. Judge the **tester's ability to execute and the coverage of the enumerated behaviors**, not case count. A small, complete plan that satisfies every *applicable* condition **passes**; do not manufacture a gap from brevity. (Conditions 1 and 7 still bind at any size: every enumerated behavior has a traceable case, and every case traces to a real upstream.)

### Step 3: Decide the verdict

- **approve** — every applicable condition passes. A tester can execute the plan as written, every enumerated upstream behavior has a traceable case, the catalog is risk-weighted, and nothing is fabricated. Approve even if you can imagine stylistic improvements; the bar is coverage + testability, not perfection — and not maximalism.
- **revise** — one or more conditions have a real, named gap (a behavior with no case, an untestable exit criterion, a case with no preconditions/steps/traces-to, a combinatorial blow-up or a thin/padded catalog, a fabricated case, a missing environment for a level, etc.).

Do not revise to signal effort or to request nice-to-haves. A condition is either met or it isn't.

### Step 4: Emit the verdict + actionable findings

Emit the verdict as a single line — the literal text `VERDICT: approve` or `VERDICT: revise`, on its own line, with **no** surrounding code fences, quotes, or extra words (the fences here are illustration only):

```
VERDICT: approve
```

Then, on the following lines, list findings. On `revise`, every finding is **actionable** — the failed condition, the exact location, and **how to fix it** — so the author can resolve it in one pass. On `approve`, findings are optional non-blocking notes; do not let them imply a revision is required.

If an **upstream was not handed in**, state that as an explicit assumption in the findings (e.g. "api-spec not provided — operation/error coverage (cond. 1) judged only against the feature-spec; provide the api-spec for a full trace") and judge the other conditions on what you have. Do not silently pass over the un-runnable coverage check, and do not default to approve.

A good finding names the gap and the fix:

> **revise** — Complete coverage (cond. 1), feature-spec behavior "user can reset password via email link": no test case in the catalog traces to it. Fix: add at least one case (happy path + the expired/invalid-link negative case, given password reset is auth-critical) with a traces-to back to this behavior.

> **revise** — Risk-weighted catalog (cond. 6), section "Filter combinations": the catalog enumerates all 64 combinations of the 6 filter toggles. Fix: replace with risk + pairwise coverage (a handful of pairwise cases plus the high-risk individual filters), not the full cross-product.

A bad finding is vague and unactionable:

> The coverage could be more thorough. *(Which behavior? Which case? What fixes it?)*

## Rules

**Hard rules (never violate):**

- **Emit exactly one verdict line, `VERDICT: approve` or `VERDICT: revise`** — that literal token, on its own line, nothing else on it. Downstream tooling parses it (a verdict-parsing contract). No alternate verdict vocabulary.
- **Judge, never author.** Return findings; do not rewrite, fix, or fill in the plan. The producer revises.
- **Single-sourced bar.** Judge against the eight conditions in Step 2 — the same bar the author produces to (the shared test-plan dossier). Do not invent extra conditions or apply a stricter private standard.
- **Coverage completeness is load-bearing.** Enumerate every behavior/operation/error from the **handed-in upstreams** and confirm each has >=1 traceable case. A behavior with no case is the highest-impact defect (cond. 1). Enumerate from whatever upstream was handed in — feature-spec/api-spec when present, else the PRD — never assume a fixed input.
- **Risk-weighted, not combinatorial, not thin.** A coverage gap, a full input-permutation cross-product, **and** a padded/thin catalog are each a `revise` (cond. 6). The catalog is exhaustive-for-the-project by risk, not the permutation cross-product and not skeletal.
- **No fabrication.** A case testing a behavior no upstream declares is a defect (cond. 7) — a real coverage gap is flagged as an assumption, not filled with an invented behavior. Spot-check cases' traces-to against the actual upstreams.
- **No false-revise.** A plan that meets every applicable condition is approved, even a thin one for a small project. Proportional sizing that still covers every enumerated behavior is not a defect. Revise only on a real, named gap.
- **No false-approve.** Never approve over a genuine gap to be agreeable. A blocking gap is a `revise`.
- **Untestable done-criteria is a gap.** An exit criterion two readers could disagree on ("testing looks good") fails condition 3 — done-criteria must be mechanically decidable.
- **Missing upstream is flagged, not silently passed.** If an upstream wasn't handed in, surface it as an explicit assumption and note that coverage of it could not be fully run; judge the rest on what you have. Never default to approve, and never invent an expectation of a document the project didn't produce.
- **Judge against the upstreams the document was given.** Assess the plan against its `depends_on` set (the upstreams the project actually produced). A **not-produced** upstream is **never** a revise trigger. But a plan that **ignored a produced upstream** it should have covered (a handed-in feature-spec whose behaviors have no cases) **is** a fair finding.
- **Every revise finding is actionable** — failed condition + location + concrete fix. No vague notes.

**Preferences (override-able):**

- Order findings by severity — coverage gaps and fabrication first, then catalog-sizing, then minor ones.
- Reference the condition number/name in each finding so the author maps it back to the bar.
- Keep approve-notes few and clearly non-blocking.

## Gotchas

- **Approving for completeness instead of executability.** Every section can be present and the plan still un-executable (cases with no preconditions, vague steps, an unobservable expected result, no traces-to). Judge whether a tester can *execute and trace it*, not whether the *template is filled*.
- **The behavior with no case.** The plan can look thorough — a long catalog, a coverage matrix — while silently missing a case for one upstream behavior. The only way to catch it is to **enumerate the upstream behaviors and tick each against the catalog** (cond. 1). This is the single most damaging and most easily-missed defect; a long catalog is not proof of coverage.
- **The combinatorial blow-up that reads as rigor.** A catalog enumerating every input permutation looks exhaustive but is unmaintainable and still misses risk-weighting — 1,024 cases for a 10-switch module is a defect, not coverage (cond. 6). Check that high-risk areas get *depth* (boundaries, negatives) and trivial areas get happy-path-only, rather than every combination everywhere.
- **The thin/padded catalog.** The opposite failure: cases that restate each other without adding coverage (padding), or a high-risk area with only a happy-path case (thin). Both fail cond. 6 even though the count looks fine. Judge depth against *risk*, not against a target number.
- **The untestable exit criterion.** "Testing complete when coverage is good" reads like a done-criterion but can't be mechanically decided — the tester can't tell when to stop (cond. 3). A real exit criterion is observable: all High-priority cases pass, no open Critical defect, every behavior has a passing traceable case.
- **The fabricated case.** A case can test a plausible-sounding behavior that **no upstream declares** — coverage of an invented requirement (cond. 7). Spot-check traces-to against the actual upstreams; a case with no real upstream backing is a defect, not coverage. A real gap should be flagged as an assumption instead.
- **Missing-upstream blind spot.** If an upstream wasn't handed in, the coverage dimension can't be fully run — do not let that absence default to an approve. Flag it as an assumption (cond. 1 partially un-runnable) and judge the rest.
- **Systematic over-flagging (false-revise).** A reviewer asked to find problems — especially one also asked to propose fixes — tends to over-correct, judging sound plans as defective. Calibrate to the bar: a condition is a gap only on a *named, real* deficiency, not on a case order or a level choice you'd have made differently. Plausible-sounding nits are the dominant reviewer error here.
- **False-revise on a proportionally-sized plan.** A thin project's plan is correctly small — a handful of cases, no performance level without an NFR, no integration tier without seams. That is right-sizing, not under-coverage. Manufacturing a gap from brevity drives avoidable revise loops; calibrate to the archetype (conditions 1 and 7 still bind: every enumerated behavior traced, nothing fabricated).
- **Confusing this with the release-runbook or design-review gate.** This judges the **QA/verification plan** (what to test, to what done-criteria). A release-runbook-review judges the operational go-to-production procedure (deploy/verify/rollback) that *reuses* this plan's exit criteria; design-review gates engineering design docs against the codebase. Don't apply an operational or a design-doc bar to the test plan.
- **Verdict token drift.** "Approved", "LGTM", "needs work", or a verdict buried mid-paragraph will not parse. Emit the literal `VERDICT: approve|revise` on its own line.

## Anti-patterns

- **Rubber-stamp approve.** Skimming the catalog's length and approving — the gate exists to catch plans a tester can't execute or that miss a behavior; a behavior with no case, a combinatorial blow-up, or an untestable exit criterion waved through becomes an escaped defect or an endless test phase.
- **Skipping the upstream enumeration.** "The catalog is long, so coverage must be fine" — without enumerating the upstream behaviors and ticking each, you miss the highest-impact defect class (cond. 1). Reviewing the catalog in isolation is the one shortcut this gate exists to forbid.
- **Counting cases instead of weighting by risk.** Treating a bigger catalog as better. The bar is risk-weighted coverage — depth where risk is, happy-path where it isn't — not maximum case count (cond. 6).
- **Nit-pick revise.** Blocking on case-ordering taste, a level choice, or nice-to-haves dressed up as gaps. Revise is for real coverage/executability blockers only.
- **Silent rewrite.** "It was easier to just add the missing case" — authoring inside a review collapses the produce/judge separation and removes the author's chance to learn the gap.
- **Inventing conditions.** Adding a private requirement the bar does not carry ("it should also include a traceability tool export / a specific test-management format") drifts the review-bar off the produce-bar and causes spurious revises. Judge the eight conditions only.
- **Maximalism.** Demanding a performance level, an integration tier, or a fuller catalog from a thin project that doesn't warrant them. The bar is the tester's ability to execute and full coverage of the enumerated behaviors, not the largest possible plan.
- **Hedged verdict.** "Mostly approve but…" or two verdict lines. Exactly one decision, exactly one token.

## Output

A single review result for one test plan:

- **One verdict line** — `VERDICT: approve` or `VERDICT: revise`, verbatim, on its own line.
- **Findings** — on `revise`, one actionable finding per blocking gap (failed condition + location + concrete fix); on `approve`, optional non-blocking notes.

The plan under review is **textual** today — strategy prose + a coverage matrix + a test-case catalog table (markdown via the local docs backend); the review **method + bar are medium-independent** (a future test-management-tool export changes only the medium, not what is judged). The **abstract consumer** is whatever orchestrates the produce->review loop: `approve` accepts the test plan for execution (and lets a release runbook reuse its exit criteria); `revise` returns the findings to the producer for a bounded revision pass.

## Related

- A **test-plan-authoring** skill (`authoring-test-plan`) — the produce half of the pair; it writes the plan to the same coverage + testability bar this skill judges against, and **owns the shared dossier** this skill reuses. Pairing them single-sources the bar so produce and review do not drift.
- The upstream **feature-spec / api-spec / PRD** — the documents every test case derives from; this gate **enumerates their behaviors/operations/errors and checks each has a traceable case** (cond. 1). Those upstreams are gated at their own authoring time, not here.
- A **release-runbook-review** skill — the gate for the operational go-to-production runbook (deploy/verify/rollback) that *reuses* this plan's exit criteria. Distinct doc, distinct bar (executability/rollback vs coverage/testability); not the QA plan.
- A **design-review** skill — the gate for engineering design documents (spec, plan, design doc, RFC, ADR), which verifies claims against the codebase. Distinct gate, distinct artifact; not the verification plan.
- A **test-plan template / content-template** tool — owns the section *structure*; this skill judges *quality against the bar*, not structural conformance.

## Progressive disclosure

- `references/sources.md` — research provenance for the review method (the single-sourced coverage + testability quality bar from the shared test-plan dossier; the ISTQB/IEEE-829/29119/NIST grounding for test levels, risk-based depth, traceability, BVA/equivalence-partitioning, and entry/exit criteria; and the reviewer-overcorrection basis for the no-false-revise discipline). Load only to audit where the guidance came from.

## Body budget

- `description` <= 1,024 chars (agentskills.io cap). Claude truncates the combined `description` + `when_to_use` at 1,536 chars in the listing.
- Body <= ~500 lines / 5,000 tokens — kept in context every turn.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k tokens, error >50k.
