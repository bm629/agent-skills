# Sources — `authoring-test-plan`

Research provenance for the method + quality bar. Primary method: deep-research (multi-source);
each major claim is corroborated by 2+ reputable sources (ISTQB Foundation, IEEE 829 /
ISO-IEC-IEEE 29119, NIST, established testing references). Findings are paraphrased, not copied.

## Test levels & test types (unit/integration/system/acceptance; functional/non-functional)

- ISTQB Foundation — Test Levels and Types: https://oboe.com/learn/istqb-foundation-level-software-testing-1qjybfg/test-levels-and-types-2
- ISTQB-based testing-types guide: https://codenote.net/en/posts/software-testing-types-istqb-guide/

## Test-plan document structure (IEEE 829 sections; scope/approach/pass-fail)

- IEEE 829 tutorial (test-doc standard, 16-clause test plan): https://zetcode.com/terms-testing/ieee-829/
- How to write a test plan with IEEE 829: https://reqtest.com/en/knowledgebase/how-to-write-a-test-plan-2/

## Risk-based testing (Likelihood x Impact drives priority + depth)

- Risk-based testing (ISTQB): https://www.leadwithskills.com/blogs/risk-based-testing-prioritizing-tests-based-on-risk-istqb
- Risk-based testing (overview): https://en.wikipedia.org/wiki/Risk-based_testing

## Coverage-by-behavior / requirements traceability

- Requirements Traceability Matrix (how-to): https://www.testrail.com/blog/requirements-traceability-matrix/
- Requirements Traceability Matrix (with example): https://www.softwaretestinghelp.com/requirements-traceability-matrix/

## Test-case design (fields, BVA, equivalence partitioning, negative testing)

- Test case template & fields (id/preconditions/steps/expected): https://www.softwaretestinghelp.com/test-case-template-examples/
- Writing effective test cases (steps vs expected): https://www.testrail.com/blog/effective-test-cases-templates/
- Boundary value analysis & equivalence partitioning: https://reqtest.com/en/knowledgebase/what-is-boundary-value-analysis-and-equivalence-partitioning/
- BVA vs equivalence partitioning: https://www.geeksforgeeks.org/software-testing/software-testing-boundary-value-analysis-vs-equivalence-partitioning/

## Exhaustive-testing-impossible / risk-weighted (not combinatorial) sizing

- ISTQB seven testing principles (exhaustive testing is impossible): https://mastersoftwaretesting.com/testing-fundamentals/software-testing-principles
- NIST combinatorial testing (why the cross-product is infeasible; pairwise): https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=910001

## Entry / exit (completion) criteria (= definition of done)

- ISTQB exit criteria glossary: https://istqb-glossary.page/exit-criteria/
- Entry and exit criteria in software testing: https://www.baeldung.com/cs/testing-entry-exit-criteria

## Standards: ISO/IEC/IEEE 29119 (current) supersedes IEEE 829

- ISO/IEC/IEEE 29119 overview (five parts; supersedes IEEE 829): https://en.wikipedia.org/wiki/ISO/IEC_29119
- ISO/IEC/IEEE 29119-3 test documentation: https://www.microtool.de/en/document-management/test-documentation-with-iso-iec-ieee-29119-32021/

## Case design: decision tables & state-transition testing

- ISTQB decision-table & state-transition testing techniques: https://oboe.com/learn/istqb-foundation-level-software-testing-1qjybfg/test-design-techniques
- Decision table testing (overview): https://en.wikipedia.org/wiki/Decision_table

## Testing ML / probabilistic systems (test-oracle problem; metamorphic; metric thresholds)

- ML Testing: Survey, Landscapes and Horizons (oracle problem, metric validation): https://arxiv.org/pdf/1906.10742
- Metamorphic testing for ML (metamorphic relations as a pseudo-oracle): https://arxiv.org/pdf/2205.00210
- T&E best practices for ML-enabled systems: https://arxiv.org/pdf/2310.06800

## Non-functional testing (performance, security, accessibility, compatibility, i18n)

- Accessibility standard — WCAG 2.2 AA (W3C): https://www.w3.org/TR/WCAG22/
- OWASP security testing (threat-derived set): https://owasp.org/www-project-web-security-testing-guide/
- ISTQB non-functional testing types: https://codenote.net/en/posts/software-testing-types-istqb-guide/

## Exploratory / session-based test management (SBTM)

- Session-Based Test Management (charters, time-boxed sessions; complements scripted): https://www.testim.io/blog/exploratory-testing/

## Test-data management (synthetic vs masked production; PII/PHI)

- Synthetic vs masked test data (hybrid strategy; PII handling): https://www.perforce.com/blog/pdx/synthetic-test-data-vs-test-data-masking

## Regression test selection / change-impact (amend)

- Impact-based + priority/risk-based + hybrid regression selection: https://www.testrail.com/blog/regression-testing/
- Requirements-based test prioritization using risk factors: https://dl.acm.org/doi/abs/10.1016/j.infsof.2015.09.002

## Note on research method

deep-research was the method; the multi-source corroboration above was gathered via WebSearch
(>= 2 reputable sources per claim, the canonical standard named where one exists — ISO/IEC/IEEE
29119, WCAG 2.2, OWASP, ISTQB). No claim relies on a single source and nothing is fabricated. The
sibling `reviewing-test-plan` skill asserts the same coverage + testability bar (its 10-condition
checklist single-sourced with this skill's Step-7) so the produce-bar and review-bar stay aligned.
