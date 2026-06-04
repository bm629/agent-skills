---
name: authoring-test-plan
description: >
  Use when authoring a test plan / QA verification plan — what to test, at what
  level, in what environment, to what done-criteria, and the cases to run. Guides
  the producer through the METHOD, not the outline: deriving every case from a
  feature-spec behavior/acceptance-criterion or an api-spec operation/error
  (never inventing one), choosing the test levels the project warrants, sizing
  the catalog by RISK-WEIGHTED coverage (more cases on high-risk areas, not the
  input-permutation cross-product), making entry/exit ("done") criteria testable,
  and pulling non-functional levels from the NFRs where handed in — to a bar
  where a tester executes the plan with no questions and every behavior has a
  traceable case. Composes with a separate test-plan template tool and
  deep-research. Consumes the handed-in upstreams (typically feature-spec +
  api-spec + PRD) — never a blank page. SPECS the cases, not the test scripts;
  not the release-runbook verification, not the behavior contract, not reviewing
  a finished one.
extensions:
  claude:
    when_to_use: "authoring the QA / verification plan (scope, levels, coverage, environments, entry/exit criteria, risk priority, test-case catalog) for a project"
    argument-hint: "<the feature-spec (+ api-spec/PRD/NFRs) to turn into a test plan>"
version: "1.0.0"
forge:
  status: reviewed
  forged: 2026-06-05
  reviewed: 2026-06-05
---

# `authoring-test-plan` — SKILL.md

> **Variant:** standard · **When to use:** authoring the QA / verification plan for a project — to a bar where a tester executes it with no further questions, every behavior has at least one traceable case, and the catalog is risk-weighted, not combinatorial.

## Overview

This skill is the *how-to* of writing a strong **test plan** (QA / verification plan) — the document that says **what to test, at what level, in what environment, to what done-criteria, and the concrete cases to run.** It spans both the **strategy** (scope, test levels & types, coverage approach, environments, entry/exit criteria, risk-based prioritization) and an enumerated **test-case catalog** (each case: id, preconditions, steps, expected result, traceability). This skill carries the producer's *judgment* — the research method and the quality bar — **not** the section list. It assumes two collaborators: a **test-plan template tool** that supplies the section *structure*, and a **deep-research capability** to ground the plan in established test-strategy practice. The producer is handed the **upstream documents** (typically the feature-spec whose behaviors the cases verify, the api-spec whose operations + errors they exercise, and the PRD whose acceptance the exit criteria tie to) — never a blank page. The bar to clear: a tester can execute the plan with no further questions — every supported behavior has at least one traceable test case, the levels and environments are stated, the exit criteria are testable, and the catalog is sized to the project by risk, not padded and not thin.

## When to activate

- Authoring a test plan / QA verification plan from an approved feature-spec (+ api-spec / PRD) that names the behaviors the system must satisfy.
- Specifying the test levels & types, coverage approach, environments, entry/exit criteria, risk prioritization, and the test-case catalog for a project.
- Filling a test-plan template with researched, traceable, risk-weighted per-behavior coverage and executable cases.

**Do NOT activate when:**

- Writing the **test automation code** (the executable pytest/Playwright/etc. scripts) — that is implementation, *downstream* of this plan. The plan specs *what* to test and the cases; it does not write the test scripts.
- Writing the **release runbook's post-deploy verification** (the operational smoke procedure) — that is a separate document; it *reuses* this plan's exit criteria, but the runbook is the operational procedure, not the QA strategy.
- Authoring the **behavior contract** itself (the feature-spec / api-spec) — those are *upstream input* here; the plan derives coverage from them, it does not redefine them.
- Reviewing or grading a finished test plan — use the runtime review gate; this skill is produce-side only.

## Inputs

Read **every document the plan hands you** — your `depends_on` set (the upstream documents discovery determined inform this one) — and derive the document's content from them. Do not hardcode a narrow single input: the typical upstreams this skill names (feature-spec + api-spec + PRD; architecture-doc / NFRs where present) are method guidance, not a cap on what you receive — the real input is whatever documents the plan hands you. Be **self-contained** — produce the plan from *whatever* context you actually receive; when an expected informing document is absent (e.g. no NFRs doc for the performance level), proceed on what you have and surface the gap as an explicit assumption, never fabricate a behavior to test. And **use a research capability where one is available** (deep-research) to ground the plan in established test-strategy practice and to size the catalog by risk-weighted coverage proportional to the project archetype, not merely to fill the template.

## Workflow

### Step 1: Take the structure from the template tool — don't invent an outline

Get the section structure from your test-plan template tool (comprehensive variant). Do **not** restate or re-derive a section list here; this skill supplies the method that *fills* those sections well. If no template is available, obtain a comprehensive test-plan structure (request/forge one, or fall back to the canonical set: scope & objectives, test levels & types, coverage approach, environments & test data, entry/exit criteria, risk-based prioritization, test-case catalog, defect/triage), then proceed.

### Step 2: Load the upstreams; build the coverage map first — derive, never invent

Read the **feature-spec** (its behaviors + acceptance criteria), the **api-spec** (its operations + error model), and the **PRD** (the success metrics the exit criteria tie to) — your **input, not a blank page**. Before any cases, build the **coverage map**: every feature-spec behavior / acceptance criterion and every api-spec operation + error case becomes a row, mapped to the test level(s) that prove it. This map is your coverage checklist — **every test case traces back to one of its rows** (no orphan/invented cases; no behavior left without a case). Where an upstream is thin or absent (e.g. no NFRs for the performance level), make the gap an **explicit assumption**, never a silently-invented behavior to test.

### Step 3: Research to ground the strategy

Use a deep-research pass to ground the plan in established **test-strategy practice** — the test levels (unit/component, integration, system/e2e, acceptance per ISTQB), the test-plan structure (IEEE 829 / ISO-IEC-IEEE 29119), **risk-based testing** (Likelihood x Impact drives priority and depth), **coverage-by-behavior** (requirements traceability), and case-design techniques (boundary value analysis, equivalence partitioning, negative testing) — for *this* product's surface, not "testing in general." **If no research capability is available, do NOT fabricate behaviors, levels, or criteria** — state them as explicitly-flagged assumptions to validate before testing.

### Step 4: Choose the levels the project warrants — map each behavior to the cheapest proving level

Not every project gets every level. Map each coverage-map row to the **cheapest level that proves it**: unit for pure logic, integration for module/service seams, system/e2e for user-visible flows, acceptance for the PRD's business criteria. Pull the **non-functional levels** (performance, security, load) from the **NFRs / architecture-doc** when handed in; **omit-with-a-note** when no NFR justifies one (do not invent a performance target to test against). Justify each level included or omitted — silent omission is a coverage gap.

### Step 5: Risk-weight the catalog — depth follows risk, not the cross-product

Exhaustive testing is impossible. Assess each in-scope area's **Likelihood x Impact** and assign a risk priority that sets its test **depth and order**:

- **Every behavior/error gets at least one traceable case** (the coverage floor).
- **High-risk / high-impact areas get MORE cases** — boundary values, equivalence-partition representatives, and negative paths (invalid input, the exact expected error/message).
- **Trivial / low-risk areas get happy-path-only.**
- The size target is **exhaustive-for-the-project by risk** — NOT the full input-permutation cross-product. A module with N on/off switches has 2^N combinations; cover it by risk + representative/pairwise selection, never all of them.

Size the whole catalog **proportionally to the archetype**: a thin CLI gets a handful of cases and collapses the non-functional levels; a large UI product gets many. Neither thin nor padded.

### Step 6: Make entry/exit criteria testable; write executable cases

- **Entry / exit ("done") criteria** are **observable/measurable**, not vague — e.g. exit = "all High-priority cases pass + no open Critical/High defect + every behavior has a passing traceable case," not "testing looks good." A reader can mechanically decide whether each is met.
- **Each catalog case** has explicit **preconditions**, **single-action steps** (verb-led: Navigate, Enter, Click, Validate — one action per step), an **expected result** = the *observable system behavior* (including the exact message/error for negative cases), and a **traces-to** back-reference to the coverage-map row it verifies.

### Step 7: Self-check against the executable-and-traceable bar before handing off

Confirm all hold (this is the bar the runtime review gate asserts — author and gate share it so they don't drift):

1. **Complete coverage** — every behavior/acceptance-criterion in the handed-in feature-spec and every operation + error in the api-spec has at least one traceable test case. No behavior left without a case.
2. **Appropriate levels** — the levels & types chosen fit the project; non-functional levels present when an NFR exists; every omission justified, not silent.
3. **Testable entry/exit criteria** — entry and exit ("done") criteria are observable/measurable, not vague.
4. **Environments + test data specified** — each level states where it runs and the data/fixtures it needs.
5. **Each catalog case is executable + traceable** — preconditions, single-action steps, an observable expected result, and a traces-to back-reference.
6. **Risk-prioritized + risk-weighted** — prioritized by Likelihood x Impact; catalog depth follows risk (more cases on high-risk, fewer on trivial), NOT the full permutation cross-product.
7. **Nothing fabricated** — every case traces to a real upstream; any coverage gap (an untestable requirement, a missing NFR) is surfaced as an explicit assumption, never filled with an invented behavior.
8. **Proportional to the archetype** — the catalog and the level set are sized to the project (thin CLI vs large UI product); exhaustive-for-the-project, not combinatorial and not skeletal.

**Thin-input gate:** if a behavior the system must satisfy cannot be researched or even credibly assumed into a testable case, surface it as a **blocker** ("behavior under-specified — needs a product/engineering decision before it can be tested") rather than inventing a case. A plan whose cases, criteria, and levels are all guesses is not executable.

## Rules

**Hard rules (never violate):**

- **Derive every case from an upstream.** Each test case traces to a feature-spec behavior/acceptance-criterion or an api-spec operation/error. No orphan/invented case; no behavior left without a case. Coverage runs off the handed-in upstreams.
- **Risk-weight the catalog, don't cross-product it.** At least one case per behavior/error; more cases (boundaries, negative paths) on high-risk areas, fewer on trivial. Never enumerate the full input-permutation cross-product.
- **Testable entry/exit criteria.** Each criterion is observable/measurable — a reader can mechanically decide if it is met. "Testing looks good" is not a criterion.
- **Each case is executable + traceable.** Preconditions, single-action verb-led steps, an observable expected result (with the exact error/message for negatives), and a traces-to back-reference.
- **Choose levels deliberately.** Map each behavior to the cheapest proving level; include non-functional levels only when an NFR justifies one; justify every omission.
- **Never fabricate.** Don't invent behaviors, levels, criteria, or NFR targets to look complete. With no source, state them as explicitly-flagged assumptions to validate before testing.
- **Compose, don't duplicate.** Take the section structure from the template tool; this skill is the method that fills it. Do not paste a competing outline.
- **Specs cases, not scripts; strategy, not the runbook.** Specify *what* to test and the cases — not the executable test code (downstream implementation), and not the release-runbook's operational verification (which reuses this plan's exit criteria).

**Preferences (override-able):**

- "Comprehensive" sets output *ambition*; stay **proportional** — completeness of the *coverage* by risk, not word count. A thin CLI collapses the non-functional levels it doesn't need.
- Prefer boundary value analysis + equivalence partitioning to choose representative values for a high-risk behavior; prefer pairwise/combinatorial selection over the full cross-product when many parameters interact.
- Prefer an exit criterion phrased against the coverage map ("every behavior has a passing traceable case") over a raw percentage.

## Gotchas

- **The catalog balloons.** Enumerating every input combination produces a combinatorial, unmaintainable catalog. Size by risk: one case per behavior, extra cases (boundaries, negatives) only where Likelihood x Impact is high.
- **A behavior with no case.** Skipping a feature-spec behavior or an api-spec error leaves a coverage hole the review gate will catch. Build the coverage map first and trace every case to it.
- **Vague exit criteria.** "Testing is done when it feels stable" can't be evaluated. Phrase every entry/exit criterion as an observable condition (cases passing, defects closed, coverage-map rows covered).
- **Inventing a performance/security target.** When no NFR is handed in, do not fabricate a latency or throughput number to test against — note the absent upstream as an assumption and omit (or flag) the non-functional level.
- **Confusing the plan with the test code.** Writing pytest/Playwright scripts here is the downstream implementation, not this document. The plan specs the cases; the scripts come after.
- **Confusing the plan with the release runbook.** The runbook's post-deploy smoke reuses this plan's exit criteria but is the operational procedure, not the QA strategy. Keep this the strategy + catalog.
- **Restating the template outline.** Re-deriving the section list inside the content (or in this skill) duplicates the template tool and drifts — fill its sections with judgment instead.

**Worked contrast — under-specified (compliant on the surface) vs executable** (use it to self-detect):

| Aspect | Under-specified (reject) | Executable (ship) |
|---|---|---|
| Coverage | "We'll test the login feature." | "FS-§3.1 *Login* + api-spec `POST /sessions` (200, 401, 429) each map to e2e + unit rows in the coverage matrix." |
| Levels | "We'll write tests." | "Unit for the token hasher; integration for the session store; e2e for the login flow; no performance level (no NFR handed in — flagged)." |
| Catalog depth | "Test all the input combinations." | "TC-001 valid login (happy); TC-002 wrong password -> `401 invalid_credentials`; TC-003 empty password (boundary); TC-004 6th attempt -> `429` (high-risk, negative)." |
| Case | "Check login works." | "Pre: a registered user. Steps: 1. POST /sessions with valid creds. Expected: `200` + a session cookie set. Traces-to: FS-§3.1." |
| Exit criteria | "Test until it's stable." | "All High-priority cases pass; no open Critical/High defect; every coverage-map row has a passing case." |

If your fill reads like the left column — true of any project, no levels, no traceability, no testable criteria — it isn't done.

## Anti-patterns

- **"I'll test every input combination to be thorough."** That's the combinatorial trap — size by risk, not the cross-product.
- **"The happy path is enough."** High-risk behaviors need boundary + negative cases; name the expected error for each.
- **"I'll invent a reasonable performance target."** No NFR, no fabricated number — flag the gap and omit the level.
- **"I'll also write the test scripts while I'm here."** The executable code is downstream implementation; this document specs the cases.
- **"Exit when it looks good."** A criterion must be mechanically evaluable; phrase it against passing cases and closed defects.
- **"I'll write the outline myself."** Duplicates the template tool — take the structure from it.
- **"Skip the research, I know testing."** The research grounds *this product's* levels, risk weighting, and case design — not testing theory.

## Output

A **comprehensive test plan** that meets the **Step 7 executable-and-traceable bar** (complete coverage with every behavior traced to at least one case; appropriate levels with omissions justified; testable entry/exit criteria; environments + test data specified; every catalog case executable and traceable; risk-prioritized and risk-weighted, not combinatorial; nothing fabricated; proportional to the archetype). The artifact is **textual** — strategy prose + a coverage matrix table + a test-case catalog table in markdown; this is not a TestRail/Xray export, and the method + bar are medium-independent (a future test-management or remote backend changes only the medium, not the method or the bar). The **abstract consumer** is the testers who execute the plan, the downstream release-runbook (which reuses its exit criteria), and a runtime review gate (which asserts the same bar). The test plan **depends on** the feature-spec + api-spec (+ PRD / NFRs where present) as input. Its *structure* comes from the template tool; this skill supplies the *content quality*.

## Related

- A **test-plan template tool** (e.g. a content/template gateway) — supplies the section structure this skill fills. Compose with it; never restate its outline.
- A **deep-research capability** — grounds the plan in established test-strategy practice (ISTQB test levels, IEEE 829 / ISO-IEC-IEEE 29119 structure, risk-based testing, requirements traceability, BVA / equivalence partitioning / negative testing).
- A **feature-spec-authoring skill** and an **api-spec-authoring skill** — produce the *upstream* behavior contracts whose behaviors + operations + errors the cases verify.
- A **PRD** and an **architecture-doc / NFRs** (where present) — upstream context: the acceptance the exit criteria tie to, and the non-functional targets the performance/security levels test against.
- A **test-plan review gate** — asserts the same executable-and-traceable bar on the finished plan at runtime; author and gate share one bar so they don't drift.
- A **release-runbook skill** — the *downstream* operational verification, a distinct document that reuses this plan's exit criteria.

## Progressive disclosure

- `references/sources.md` — research provenance for the method + quality bar (ISTQB test levels & principles, IEEE 829 test-plan structure, risk-based testing, requirements traceability, test-case design techniques, entry/exit criteria). Load only to audit where the guidance came from.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap).
- Body ≤ ~500 lines / 5,000 tokens.
- Heavy content lives in `references/`, loaded on demand.
