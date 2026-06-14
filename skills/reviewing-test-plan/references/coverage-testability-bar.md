# Coverage + testability bar — per-condition pass/gap signals

Loaded on demand. The body's Step-2 carries the ten conditions; this file carries the pass/gap signals + a worked finding per condition, with extra depth on the deepened (3/4/5) and new (9/10) conditions. The bar is single-sourced with `authoring-test-plan` Step-7.

## 1. Complete coverage (binds at any size)

- **Pass:** every enumerated feature-spec behavior/AC + api-spec operation/error (else PRD requirement) has >=1 case with a traces-to.
- **Gap:** an enumerated upstream item with no case. The highest-impact, most-easily-missed defect — a long catalog is not proof; tick each upstream item against the catalog.

## 2. Appropriate functional levels (functional only — non-functional is cond. 9)

- **Pass:** unit/integration/e2e/acceptance present as warranted; omissions justified.
- **Gap:** a clearly-warranted functional level absent with no rationale (e.g. no integration cases for a multi-service system).
- **Proportionality:** a thin project collapses levels it doesn't need.

## 3. Testable entry/exit criteria (deepened: coverage floor + open-defect threshold)

- **Pass:** exit is mechanically decidable — ties to a coverage floor ("every behavior has a passing traceable case") AND an open-defect threshold ("no open Critical/High"); coverage phrased against requirements/risk.
- **Gap:** vague criteria ("testing looks good"); a bare code-coverage % as the gate (a script metric that says nothing about which behaviors are tested); no defect threshold.
- **Worked:** *revise — cond. 3: exit reads "stop when coverage is good". Fix: "all High cases pass + every coverage-map row has a passing case + no open Critical/High defect".*

## 4. Environments + test data (deepened: test-data management)

- **Pass:** each level names its environment + the data it needs + provisioning/reset + sensitive-data (PII/PHI) handling (synthetic vs masked-production).
- **Gap:** a level with no environment; cases assuming fixtures the plan never specifies; raw production PII in a test environment.
- **Proportionality:** a thin plan = one env, simple fixtures — not a gap.

## 5. Executable + traceable cases (deepened: ML metric-threshold)

- **Pass:** preconditions + single-action steps + observable expected result + traces-to. For an ML/probabilistic case, the expected result is a **metric-threshold on a named dataset** (e.g. "precision@10 >= 0.85 on `rec-eval-v2`") or a metamorphic relation.
- **Gap:** missing preconditions; vague/multi-action steps; a non-observable expected result; no traces-to; an ML case worded "the model is accurate" / "results are relevant" (the un-runnable result — recognize the probabilistic case, accept a metric-threshold; this is NOT a new bar beyond cond. 5).

## 6. Risk-prioritized + risk-weighted (case-design techniques are author aids)

- **Pass:** Likelihood x Impact drives depth; high-risk areas get boundaries/negatives (via BVA/EP/decision-table/state-transition/pairwise — judged by outcome); trivial areas get happy-path.
- **Gap (three directions):** coverage gap (too few for the risk); combinatorial blow-up (every permutation — 1,024 cases for a 10-switch module); padded/thin (cases that don't add coverage, or a high-risk area with only a happy path).
- **Never** demand a literal decision table / pairwise table — judge the outcome.

## 7. No fabrication (binds at any size)

- **Pass:** every case traces to a real upstream; gaps flagged as explicit assumptions.
- **Gap:** a case testing a behavior no upstream declares. Spot-check a sample of traces-to against the actual upstreams.

## 8. Proportional to the archetype

- **Pass:** sized to the project; a small complete plan satisfying every applicable condition passes.
- **Gap:** skeletal for the archetype (a broad product with a handful of cases) or combinatorial (cond. 6). Right-sizing is NOT a gap.

## 9. Non-functional testing (NEW — warranted types carry numeric targets; proportional)

- **Pass:** each non-functional type the NFRs/archetype **warrant** has a checkable approach + a numeric/standard target — performance (load profile + p95/throughput + tool), security (a threat-derived set), accessibility (**WCAG 2.2 AA**), usability, compatibility (a matrix), i18n/l10n.
- **Gap:** a warranted type present with no approach/target ("we'll test performance" with no profile/target); an NFR with no non-functional testing covering it.
- **Proportionality (load-bearing):** a thin project with no NFR warrants **none** — absence is NOT a gap; never demand a type the archetype doesn't warrant; never fabricate a target.
- **No double-count:** cond. 9 owns the non-functional axis; cond. 2 is functional-only. A missing warranted perf level is ONE finding (cond. 9), not two.
- **Worked:** *revise — cond. 9: NFR-A11Y requires WCAG 2.2 AA but the plan has no accessibility approach. Fix: add an accessibility row — automated scan + keyboard/contrast/focus-appearance manual checks against WCAG 2.2 AA.*

## 10. Delta-scoped amend (NEW — only when a change request is handed in)

- **Detect:** a change request/delta against an existing plan is in the input. Greenfield (no change request) -> **n/a**, never a gap.
- **Pass:** the delta is in-scope + edit-not-redraw; the coverage map was re-traced (changed behaviors re-mapped, removed ones retired, no behavior left without a case); the regression set was selected by **impact + risk** (not all, not none); a discovered-defect amend added a traced regression case; the plan's own version + changelog is present + superseded cases marked; the touched cases still meet conds. 5–6.
- **Gap:** a silent redraw; a changed behavior left without a re-traced case; regression selection skipped or "re-run everything"; no version/changelog.
- **Scope:** judge the delta + coverage/trace integrity + regression selection — NOT a full re-review of the unchanged plan.
- **Worked:** *revise — cond. 10: the change request alters "apply a coupon at checkout" but the catalog wasn't re-traced and no regression set was named. Fix: re-map the coupon coverage row + adjust its case, and select the impact+risk regression set (the cart + pricing cases that depend on coupons).*

## The no-false-revise / inventing-conditions discipline

A condition is a gap only on a *named, real* deficiency. Do NOT: revise on case-ordering taste or a level choice you'd have made differently; demand the author aids (decision tables, exploratory/SBTM, metamorphic testing) as conditions — they are judged by OUTCOME (cond. 1/5/6/9), never by literal use; demand a non-functional type a thin archetype doesn't warrant (cond. 9 proportional); manufacture a gap from brevity (a thin-but-complete plan passes; conds. 1/5/7 still bind). Every revise finding is actionable: failed condition + location + concrete fix.
