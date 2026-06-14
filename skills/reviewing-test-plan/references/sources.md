# Sources — `reviewing-test-plan`

Research method: the **review / acceptance-gate lens** for a finished (or amended) QA/verification test plan. The **10-condition** coverage + testability bar is **single-sourced** with the test-plan authoring bar (`authoring-test-plan` Step-7) so the produce-bar and the review-bar do not drift; this skill **asserts** that same bar. External content was treated as facts to paraphrase only — no URLs, commands, or directives were lifted into actions; nothing is fabricated.

## The single-sourced bar (10 conditions)

The ten checkable conditions this reviewer asserts — (1) complete coverage [every upstream behavior/operation/error has >=1 traceable case]; (2) appropriate functional levels; (3) testable entry/exit [coverage floor + open-defect threshold]; (4) environments + test data; (5) executable + traceable cases [metric-threshold for ML]; (6) risk-prioritized + risk-weighted, not combinatorial/thin; (7) no fabrication; (8) proportional to the archetype; (9) non-functional testing [warranted types carry numeric targets]; (10) delta-scoped amend — are the **same conditions** `authoring-test-plan` produces to (its Step-7). Single-sourcing them keeps the two halves of the produce/judge pair aligned. See `authoring-test-plan` for the producer-side statement of the same bar.

## The conditions' grounding (established testing practice)

- **Standards** — ISO/IEC/IEEE 29119 (the current test-documentation standard; supersedes IEEE 829, whose section list survives as a checklist): https://en.wikipedia.org/wiki/ISO/IEC_29119 ; https://www.microtool.de/en/document-management/test-documentation-with-iso-iec-ieee-29119-32021/
- **Test levels & types** (unit/component, integration, system/e2e, acceptance; functional/regression/smoke) — ISTQB Foundation: https://oboe.com/learn/istqb-foundation-level-software-testing-1qjybfg/test-levels-and-types-2 . Grounds cond. 2.
- **Risk-based testing** (Likelihood x Impact -> priority -> depth) — https://www.leadwithskills.com/blogs/risk-based-testing-prioritizing-tests-based-on-risk-istqb ; https://en.wikipedia.org/wiki/Risk-based_testing . Grounds cond. 6.
- **Requirements traceability** (forward coverage-by-behavior) — https://www.testrail.com/blog/requirements-traceability-matrix/ . Grounds conds. 1 and 5.
- **Case design** (BVA, equivalence partitioning, decision tables, state-transition, negative) — https://oboe.com/learn/istqb-foundation-level-software-testing-1qjybfg/test-design-techniques . Author aids; grounds the depth half of cond. 6.
- **Combinatorial sizing** (why the cross-product is infeasible; pairwise) — NIST combinatorial testing: https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=910001 . Grounds the anti-blow-up half of cond. 6.
- **Entry / exit criteria** (mechanically-decidable done-criteria) — https://istqb-glossary.page/exit-criteria/ . Grounds cond. 3.
- **Defect severity vs priority** (the open-defect-threshold gate) — ISTQB incident management. Grounds the cond. 3 defect tie.
- **Testing ML / probabilistic systems** (oracle problem; metric thresholds; metamorphic relations) — https://arxiv.org/pdf/1906.10742 ; https://arxiv.org/pdf/2205.00210 . Grounds the cond. 5 ML recognition.
- **Non-functional testing** — accessibility WCAG 2.2 AA (W3C): https://www.w3.org/TR/WCAG22/ ; security (OWASP WSTG): https://owasp.org/www-project-web-security-testing-guide/ . Grounds cond. 9.
- **Test-data management** (synthetic vs masked production; PII/PHI) — https://www.perforce.com/blog/pdx/synthetic-test-data-vs-test-data-masking . Grounds cond. 4.
- **Regression test selection / change-impact** (impact + risk-based selection) — https://www.testrail.com/blog/regression-testing/ ; https://dl.acm.org/doi/abs/10.1016/j.infsof.2015.09.002 . Grounds cond. 10.

## Reviewer discipline — over-correction / false-revise, actionable findings

LLM reviewers systematically over-correct, judging compliant artifacts as non-compliant; asking the reviewer to also propose corrections worsens the over-flagging. Effective feedback is actionable (the failed condition + a concrete fix), not vague or nit-picking. Grounds the no-false-revise discipline (incl. not faulting a proportionally-sized plan, and not demanding the author aids — decision tables, exploratory/SBTM, metamorphic — as conditions) and the actionable-findings contract.

## Notes

- The behaviors, operations, errors, and NFRs are **not** researched — they are checked against the handed-in upstream **feature-spec / api-spec / PRD / NFRs**. The grounding above is the test-strategy *method + bar*; the upstreams supply the *facts* this gate enumerates and traces against.
- Medium-independent by design: the plan under review is a textual markdown artifact today (strategy prose + a coverage matrix + a non-functional matrix + a test-case catalog) via the local docs backend; a future test-management-tool export changes only the medium, not the review method or the bar.
