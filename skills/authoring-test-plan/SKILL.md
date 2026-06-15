---
name: authoring-test-plan
description: >
  Use when authoring or amending a test plan / QA verification plan — what to
  test, at what level, to what done-criteria, and the cases to run. Guides the
  METHOD, not the outline: deriving every case from a feature-spec behavior/AC
  or api-spec operation/error (never inventing one); the functional levels the
  project warrants; RISK-WEIGHTED catalog sizing
  (BVA/equivalence/decision-table/state-transition/pairwise, not the
  cross-product); a non-functional taxonomy (perf/security/accessibility WCAG
  2.2 AA/compat/i18n) each with a numeric target where warranted;
  metric-threshold-on-a-named-dataset cases for ML/probabilistic behavior; and
  amending as a versioned delta with impact+risk regression selection — to a bar
  where a tester executes it with no questions, every behavior traced. Composes
  with a template tool + deep-research; consumes
  handed-in upstreams (feature-spec/api-spec/PRD/NFRs), never a blank page. Specs
  the cases, not the scripts; not the runbook, not the behavior contract, not
  reviewing one.
extensions:
  claude:
    when_to_use: "authoring or amending the QA / verification plan (scope, functional levels, coverage, non-functional taxonomy, environments + test data, entry/exit criteria, risk priority, test-case catalog) for a project"
    argument-hint: "<the feature-spec (+ api-spec/PRD/NFRs) to turn into a test plan, or the existing plan + change request to amend>"
version: "1.1.0"
forge:
  status: reviewed
  forged: 2026-06-05
  reviewed: 2026-06-15
---

# `authoring-test-plan` — SKILL.md

> **Variant:** standard · **When to use:** authoring (or amending) the QA / verification plan for a project — to a bar where a tester executes it with no further questions, every behavior has at least one traceable case, the catalog is risk-weighted not combinatorial, and the warranted non-functional testing carries numeric targets.

## Overview

This skill is the *how-to* of writing a strong **test plan** (QA / verification plan) — the document that says **what to test, at what level, in what environment, with what data, to what done-criteria, and the concrete cases to run.** It spans the **strategy** (scope, functional test levels & types, coverage approach, non-functional testing, environments + test data, entry/exit criteria, risk-based prioritization) and an enumerated **test-case catalog** (each case: id, preconditions, steps, expected result, traceability), plus **amending** an approved plan as a versioned delta. This skill carries the producer's *judgment* — the research method and the quality bar — **not** the section list. It assumes two collaborators: a **test-plan template tool** that supplies the section *structure*, and a **deep-research capability** to ground the plan in established test-strategy practice. The producer is handed the **upstream documents** (typically the feature-spec whose behaviors the cases verify, the api-spec whose operations + errors they exercise, the PRD whose acceptance the exit criteria tie to, and the NFRs/architecture-doc the non-functional testing targets) — never a blank page. The bar: a tester executes the plan with no further questions — every supported behavior has a traceable case, the levels + environments + data are stated, the exit criteria are testable, the warranted non-functional testing carries numeric targets, and the catalog is sized by risk, not padded and not thin.

## When to activate

- Authoring a test plan / QA verification plan from an approved feature-spec (+ api-spec / PRD / NFRs) that names the behaviors the system must satisfy.
- Specifying the functional levels & types, coverage approach, non-functional testing, environments + test data, entry/exit criteria, risk prioritization, and the test-case catalog.
- **Amending** an approved plan against a change request (an upstream behavior changed/added/removed, or a discovered defect) — a versioned delta, not a redraw (see Step 8).
- Filling a test-plan template with researched, traceable, risk-weighted per-behavior coverage and executable cases.

**Do NOT activate when:**

- Writing the **test automation code** (the executable pytest/Playwright/etc. scripts) — that is implementation, *downstream* of this plan. The plan specs *what* to test and the cases; it does not write the scripts.
- Writing the **release runbook's post-deploy verification** (the operational smoke procedure) — a separate document that *reuses* this plan's exit criteria, not the QA strategy.
- Authoring the **behavior contract** itself (the feature-spec / api-spec) — those are *upstream input*; the plan derives coverage from them, it does not redefine them.
- Reviewing or grading a finished test plan — use `reviewing-test-plan` (the twin gate); this skill is produce-side only.

## Inputs

Read **every document the plan hands you** — your `depends_on` set (the upstreams discovery determined inform this one) — and derive the content from them. Don't hardcode a narrow input: the typical upstreams (feature-spec + api-spec + PRD; architecture-doc / NFRs where present) are method guidance, not a cap — the real input is whatever documents the plan hands you. Be **self-contained**: produce the plan from *whatever* context you receive; when an expected informing document is absent (e.g. no NFRs doc for the performance approach), proceed on what you have and surface the gap as an **explicit assumption**, never fabricate a behavior or a target. **Use a research capability where available** (deep-research) to ground the plan in established test-strategy practice and size the catalog by risk-weighted coverage proportional to the archetype. For an **amend**, the input also includes the **existing plan + the change request**.

## Workflow

### Step 1: Take the structure from the template tool — don't invent an outline

Get the section structure from your test-plan template tool (comprehensive variant). Do **not** restate or re-derive a section list here; this skill supplies the method that *fills* those sections. The comprehensive template homes: scope, functional levels & types, the coverage matrix, environments, entry/exit, risk prioritization, the case catalog, defect/triage, **versioning & changelog, a non-functional testing matrix, test-data management, and regression/change-impact**. If no template is available, request/forge one, or fall back to that canonical set, then proceed.

### Step 2: Load the upstreams; build the coverage map first — derive, never invent

Read the **feature-spec** (behaviors + acceptance criteria), the **api-spec** (operations + error model), and the **PRD** (the success metrics the exit criteria tie to) — your **input, not a blank page**. Before any cases, build the **coverage map**: every feature-spec behavior / acceptance criterion and every api-spec operation + error case becomes a row, mapped to the test level(s) that prove it. This map is your coverage checklist — **every test case traces back to one of its rows** (no orphan/invented case; no behavior left without a case). This is the load-bearing standout. Phrase coverage and the exit criterion against **requirements + risk coverage** (every behavior exercised; high-risk areas covered to depth) — **not a bare code-coverage %** (a script metric, measured downstream, that says nothing about whether each behavior is tested). Where an upstream is thin or absent, make the gap an **explicit assumption**, never a silently-invented behavior.

### Step 3: Research to ground the strategy

Use a deep-research pass to ground the plan in established **test-strategy practice** — the test levels (unit/component, integration, system/e2e, acceptance per ISTQB), the test-plan structure (**ISO/IEC/IEEE 29119**, the current standard; IEEE 829 is superseded but its section list survives as a readable checklist), the **test-type taxonomy** (functional / regression / smoke-sanity / structural), **risk-based testing** (Likelihood x Impact drives priority + depth), **requirements-coverage traceability**, and case-design techniques (BVA, equivalence partitioning, decision tables, state-transition testing, pairwise selection, negative testing) — for *this* product's surface, not "testing in general." If no research capability is available, do **NOT** fabricate behaviors, levels, or criteria — state them as explicitly-flagged assumptions to validate.

### Step 4: Choose the functional levels the project warrants — cheapest proving level

Not every project gets every level. Map each coverage-map row to the **cheapest level that proves it**: unit for pure logic, integration for module/service seams, system/e2e for user-visible flows, acceptance for the PRD's business criteria. Choose the warranted **types** (regression, smoke/sanity) deliberately. Justify each level/type included or omitted — silent omission is a coverage gap.

### Step 5: Risk-weight the catalog + design cases — depth follows risk, not the cross-product

Exhaustive testing is impossible. Assess each in-scope area's **Likelihood x Impact** → a risk priority that sets test **depth and order**:

- **Every behavior/error gets at least one traceable case** (the coverage floor).
- **High-risk areas get MORE cases** — chosen with the technique that fits: **BVA** (at/around boundaries), **equivalence partitioning** (one per class), **decision tables** (combinatorial rules), **state-transition testing** (stateful behavior), **pairwise selection** (many interacting parameters → cover all pairs, not 2^N), **negative testing** (the exact expected error).
- **Trivial / low-risk areas get happy-path-only.**
- **ML / probabilistic behavior:** a deterministic "expected result" mis-fits a model with no fixed output (the *test-oracle problem*). Such a case is **metric-threshold on a NAMED dataset** (e.g. "precision >= 0.92 on `eval-v3`") or a **metamorphic relation** — never "the model is accurate". Add drift / fairness checks where warranted. (Depth: `references/case-design-and-nonfunctional.md`.)
- Optionally complement scripted cases with **chartered, time-boxed exploratory (SBTM) sessions** where automation is not cost-effective — a charter (mission + areas + time box), not ad-hoc clicking.

The size target is **exhaustive-for-the-project by risk** — NOT the full input-permutation cross-product (a module with N switches has 2^N combinations; cover by risk + pairwise). Proportional to the archetype: a thin CLI gets a handful and collapses the levels it doesn't need; a large UI product gets many.

### Step 6: Non-functional testing, environments + test data, testable criteria, executable cases

- **Non-functional testing (proportional).** For each non-functional type an NFR / the archetype **warrants**, state a checkable approach + a **numeric/standard target**: performance (a load profile + p95/throughput + tool), security (a threat-derived set), accessibility (**WCAG 2.2 AA**), usability, compatibility (a matrix), i18n/l10n. **Omit a type with a one-line note** when no NFR warrants it — never invent a latency number. (Depth: `references/case-design-and-nonfunctional.md`.)
- **Environments + test data.** Each level states **where** it runs and the **data** it needs. Manage test data deliberately: synthetic vs masked-production, **PII/PHI handling** (no raw production PII in a test env), fixture lifecycle (provision + reset), data-driven testing. (Depth: `references/execution-and-amend.md`.)
- **Entry / exit ("done") criteria** are **observable/measurable** — exit = "all High-priority cases pass + every behavior has a passing traceable case + the warranted non-functional targets met + **no open Critical/High defect**" (a defect severity-vs-priority scale + the open-defect threshold make "done" mechanically decidable), not "testing looks good".
- **Each catalog case** has explicit **preconditions**, **single-action verb-led steps** (Navigate, Enter, Click, Validate — one action per step), an **observable expected result** (the exact message/error for negatives; the metric gate for an ML case), and a **traces-to** back-reference to its coverage-map row.

### Step 7: Self-check against the bar before handing off

Confirm all hold (this is the bar the `reviewing-test-plan` gate asserts — author and gate share it so they don't drift):

1. **Complete coverage** — every feature-spec behavior/AC + every api-spec operation/error has >=1 traceable case. No behavior without a case.
2. **Appropriate functional levels** — unit/integration/e2e/acceptance fit the project; every omission justified, not silent.
3. **Testable entry/exit criteria** — observable/measurable; the exit ties to a coverage floor + an open-defect threshold; coverage phrased against requirements/risk, not a bare code-cov %.
4. **Environments + test data specified** — each level states where it runs + the data it needs + how it's provisioned/reset + sensitive-data handling.
5. **Each case executable + traceable** — preconditions, single-action steps, an observable expected result (or a metric-threshold for ML), and a traces-to.
6. **Risk-prioritized + risk-weighted** — Likelihood x Impact; depth follows risk (boundaries/negatives on high-risk); NOT the permutation cross-product; not thin/padded.
7. **Nothing fabricated** — every case traces to a real upstream; a gap is an explicit assumption, never an invented behavior/target.
8. **Proportional to the archetype** — sized to the project; exhaustive-for-the-project, not combinatorial and not skeletal.
9. **Non-functional testing** — each warranted non-functional type carries a checkable approach + a numeric/standard target; an inapplicable type is omitted with a note.
10. **Amend (if amending)** — the delta is scoped + edit-not-redraw, the coverage map re-traced, the regression set selected by impact+risk, the plan versioned + changelogged, superseded cases marked (Step 8).

**Thin-input gate:** if a behavior the system must satisfy cannot be researched or even credibly assumed into a testable case, surface it as a **blocker** ("behavior under-specified — needs a product/engineering decision before it can be tested") rather than inventing a case.

### Step 8: Amend an approved plan (versioned delta — not a redraw)

When handed an **existing plan + a change request** (an upstream behavior changed/added/removed, or a discovered defect):

1. **Scope** the change — the coverage-map row(s), case(s), level/type, criterion, or non-functional approach it touches.
2. **Edit, don't redraw** — amend the affected rows/cases in place.
3. **Re-trace the coverage map** — a changed/added behavior re-maps its row(s); a removed behavior retires its case(s); coverage integrity holds (no behavior without a case, no orphan case).
4. **Select the regression set by impact + risk** — the existing cases that must re-run because they touch the changed area (impact-based) + the high-risk/high-value ones (risk-based) — not all, not none; justified.
5. **Defect → regression case** — a discovered defect earns >=1 new case traced to the behavior it broke, so it can't silently recur.
6. **Version + changelog** the plan's own version (who/when/what/why); **mark superseded/retired cases** (don't silently delete). (Depth: `references/execution-and-amend.md`.)

## Rules

**Hard rules (never violate):**

- **Derive every case from an upstream.** Each case traces to a feature-spec behavior/AC or an api-spec operation/error. No orphan/invented case; no behavior without a case.
- **Risk-weight the catalog, don't cross-product it.** >=1 case per behavior; more cases (boundaries, negatives) on high-risk areas via the fitting technique (BVA/EP/decision-table/state-transition/pairwise); never the full permutation cross-product.
- **Testable entry/exit criteria.** Each is observable/measurable — a reader can mechanically decide it. Tie the exit to a coverage floor + an open-defect threshold. "Testing looks good" is not a criterion.
- **Each case is executable + traceable.** Preconditions, single-action verb-led steps, an observable expected result (the exact error for negatives; a metric-threshold-on-a-named-dataset for ML — never "the model works"), and a traces-to.
- **Non-functional testing is targeted, not vague.** Each warranted non-functional type carries a checkable approach + a numeric/standard target (perf p95, WCAG 2.2 AA, a threat set); omit an inapplicable type with a note.
- **Never fabricate.** Don't invent behaviors, levels, criteria, or NFR/latency targets to look complete. With no source, state them as explicitly-flagged assumptions.
- **Amend as a versioned delta.** On a change request, edit-not-redraw, re-trace coverage, select the regression set by impact+risk, version + changelog, mark superseded — never a silent full rewrite.
- **Compose, don't duplicate.** Take the section structure from the template tool; this skill is the method that fills it. Don't paste a competing outline.
- **Specs cases, not scripts; strategy, not the runbook.** Specify *what* to test and the cases — not the executable test code (downstream), and not the release-runbook's operational verification.

**Preferences (override-able):**

- "Comprehensive" sets *ambition*; stay **proportional** — completeness of *coverage* by risk, not word count. A thin CLI collapses the non-functional matrix, regression, and changelog it doesn't need.
- Prefer BVA + equivalence partitioning for representative values; decision tables for combinatorial rules; state-transition coverage for stateful behavior; pairwise over the cross-product when parameters interact.
- Prefer an exit criterion phrased against the coverage map ("every behavior has a passing traceable case") over a raw percentage.

## Gotchas

- **The catalog balloons.** Enumerating every input combination is combinatorial and unmaintainable. Size by risk: one case per behavior, extra cases (boundaries, negatives) only where Likelihood x Impact is high; pairwise when parameters interact.
- **A behavior with no case.** Skipping a feature-spec behavior or an api-spec error leaves a coverage hole the gate will catch. Build the coverage map first and trace every case to it.
- **Vague exit criteria.** "Done when it feels stable" can't be evaluated. Phrase every criterion observably (cases passing, defects closed, coverage-map rows covered).
- **"The model is accurate" on an ML feature.** A non-deterministic system has no fixed oracle — a deterministic pass/fail case is un-runnable. Use a metric-threshold on a named dataset (or a metamorphic relation).
- **Inventing a performance/accessibility target.** No NFR → no fabricated latency/throughput number — note the absent upstream and omit (or flag) the type. Accessibility's standard target is WCAG 2.2 AA.
- **Code coverage as the exit gate.** "90% coverage" is a script metric, gameable, and says nothing about whether each behavior is tested. Gate on requirements + risk coverage.
- **Amend by redraw.** Regenerating the whole plan on a small change loses the audit trail and the regression-selection discipline. Scope it, edit in place, version it.
- **Confusing the plan with the test code / the release runbook.** The scripts are downstream implementation; the runbook's smoke reuses this plan's exit criteria but is the operational procedure. Keep this the strategy + catalog.
- **Restating the template outline.** Re-deriving the section list duplicates the template tool and drifts — fill its sections with judgment.

**Worked contrast — under-specified (compliant on the surface) vs executable** (use it to self-detect):

| Aspect | Under-specified (reject) | Executable (ship) |
|---|---|---|
| Coverage | "We'll test the login feature." | "FS-§3.1 *Login* + api-spec `POST /sessions` (200, 401, 429) each map to e2e + unit rows in the coverage matrix." |
| Levels | "We'll write tests." | "Unit for the token hasher; integration for the session store; e2e for the login flow." |
| Catalog depth | "Test all the input combinations." | "TC-001 valid login (happy); TC-002 wrong password -> `401`; TC-003 empty password (boundary); TC-004 6th attempt -> `429` (high-risk negative)." |
| ML case | "Verify the recommender is accurate." | "Pre: dataset `rec-eval-v2`. Expected: precision@10 >= 0.85 AND p95 latency <= 120ms. Traces-to: FS-§4.2." |
| Non-functional | "It should be fast and accessible." | "Performance: 500 concurrent users, p95 <= 200ms (k6). Accessibility: WCAG 2.2 AA — keyboard + contrast + focus-appearance." |
| Exit criteria | "Test until it's stable." | "All High-priority cases pass; no open Critical/High defect; every coverage-map row has a passing case." |

If your fill reads like the left column — true of any project, no levels, no traceability, no targets — it isn't done.

## Anti-patterns

- **"I'll test every input combination to be thorough."** The combinatorial trap — size by risk + pairwise, not the cross-product.
- **"The happy path is enough."** High-risk behaviors need boundary + negative cases; name the expected error.
- **"I'll invent a reasonable performance target."** No NFR, no fabricated number — flag the gap and omit the type.
- **"A deterministic pass/fail is fine for the model."** ML needs a metric-threshold on a named dataset or a metamorphic relation, not a fixed expected value.
- **"I'll just regenerate the whole plan for this change."** Amend is a scoped, versioned delta with impact+risk regression selection.
- **"I'll also write the test scripts while I'm here."** The executable code is downstream implementation; this document specs the cases.
- **"Exit when it looks good."** A criterion must be mechanically evaluable; phrase it against passing cases + closed defects.
- **"I'll write the outline myself."** Duplicates the template tool — take the structure from it.
- **"Skip the research, I know testing."** The research grounds *this product's* levels, risk weighting, non-functional targets, and case design — not testing theory.

## Output

A **comprehensive test plan** that meets the **Step 7 bar** (complete traceable coverage; appropriate functional levels; testable entry/exit tied to a defect threshold; environments + test-data management; executable + traceable cases incl. metric-threshold ML cases; risk-weighted not combinatorial; warranted non-functional testing with numeric targets; nothing fabricated; proportional; and, when amending, a scoped versioned delta with impact+risk regression selection). The artifact is **textual** — strategy prose + a coverage matrix + a non-functional matrix + a test-case catalog in markdown; not a TestRail/Xray export, and the method + bar are medium-independent (a future test-management backend changes only the medium). The **abstract consumer** is the testers who execute it, the downstream release-runbook (which reuses its exit criteria), and the `reviewing-test-plan` gate (which asserts the same bar). The plan **depends on** the feature-spec + api-spec (+ PRD / NFRs where present). Its *structure* comes from the template tool; this skill supplies the *content quality*.

## Related

- A **test-plan template tool** (e.g. `content-template-gateway`) — supplies the section structure this skill fills (incl. the non-functional, versioning, test-data, and regression homes). Compose with it; never restate its outline.
- A **deep-research capability** — grounds the plan in established practice (ISTQB levels, ISO/IEC/IEEE 29119 structure, risk-based testing, requirements traceability, BVA/EP/decision-table/state-transition/pairwise, ML testing, WCAG 2.2 AA).
- **`reviewing-test-plan`** — the twin gate; it asserts the same coverage + testability bar (the 10-condition checklist single-sourced with this skill's Step-7), so produce and review do not drift.
- A **feature-spec-authoring** + an **api-spec-authoring** skill — produce the *upstream* behavior contracts the cases verify.
- A **PRD** + an **architecture-doc / NFRs** — upstream context: the acceptance the exit criteria tie to, and the non-functional targets the §10 testing exercises.
- A **release-runbook skill** — the *downstream* operational verification, a distinct document that reuses this plan's exit criteria.

## Progressive disclosure

- `references/case-design-and-nonfunctional.md` — the case-design techniques (BVA, equivalence partitioning, decision tables, state-transition testing, pairwise) + exploratory/SBTM, the non-functional testing taxonomy (per-type approach + target), and ML/probabilistic case design (metric-threshold, metamorphic, drift/fairness).
- `references/execution-and-amend.md` — test-data management (synthetic vs masked, PII/PHI, fixtures, data-driven), defect severity/priority + the exit tie, and the amend / regression-selection procedure.
- `references/sources.md` — research provenance for the method + quality bar. Load only to audit where the guidance came from.

## Body budget

- `description` <= 1,024 chars (agentskills.io cap).
- Body <= ~500 lines / 5,000 tokens.
- Heavy content lives in `references/`, loaded on demand.

## Changelog

- **1.1.0** (2026-06-15) — production-grade restructure: added the iteration/amend method (Step 8), a non-functional testing taxonomy with numeric targets (perf/security/WCAG 2.2 AA/compat/i18n), ML/probabilistic case design (metric-threshold/metamorphic), the case-design technique set (BVA/EP/decision-table/state-transition/pairwise) + exploratory/SBTM, the coverage-criteria taxonomy + coverage-based exit, test-data management, and defect severity-vs-priority; named ISO/IEC/IEEE 29119 as the current standard (IEEE 829 superseded); pushed depth to two new `references/` files. Additive — input contract + the textual artifact unchanged. Single-sourced with `reviewing-test-plan` 1.1.0 (10-condition bar).
- **1.0.0** (2026-06-05) — initial reviewed release.
