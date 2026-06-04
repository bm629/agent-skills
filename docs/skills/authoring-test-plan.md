# authoring-test-plan

Author a **test plan / QA verification plan** — what to test, at what level, in what environment, to what done-criteria, and the concrete cases to run: scope and objectives, test levels and types, a coverage approach traced to the behaviors, environments and test data, entry/exit criteria, risk-based prioritization, and an enumerated test-case catalog. The how-to (a test-strategy method + a coverage/testability bar), composed with a separate test-plan template tool and a deep-research capability; targets a textual markdown artifact (strategy prose + a coverage matrix table + a test-case catalog table).

## Purpose

A test plan is the agreement on how a system's behavior gets verified before it ships. This skill carries the producer's judgment — not the section list — guiding a producer to derive every test case from a feature-spec behavior/acceptance-criterion or an api-spec operation/error (never inventing one), choose the test levels the project warrants (unit/integration/e2e/performance/security/manual), size the catalog by risk-weighted coverage rather than the input-permutation cross-product, make entry/exit ("done") criteria testable, and pull the non-functional levels from the NFRs where handed in. The bar to clear: a tester executes the plan with no further questions, every behavior has at least one traceable case, and the catalog is sized to the project — neither thin nor a combinatorial blow-up.

## When to activate

- Authoring a QA/verification plan from the handed-in upstreams (typically feature-spec + api-spec + PRD).
- Specifying the scope, levels, coverage, environments, entry/exit criteria, and the test-case catalog of a verification effort.
- Filling a test-plan template with researched, decision-complete, traceable per-case content.

### When NOT to activate

- **The test automation code / framework** -> the plan specs *what* to test and the cases; it does not write the executable test scripts (that is implementation, downstream).
- **The release runbook's verification** -> `authoring-release-runbook` (it reuses this plan's exit criteria).
- **The behavior contract itself** -> `authoring-feature-spec` / `authoring-api-spec` (the test-plan derives coverage from them).
- **Reviewing a finished test plan** -> `reviewing-test-plan`.

## Workflow

Take the section structure from the test-plan template tool (don't invent an outline). Read the full handed-in `depends_on` set; the feature-spec behaviors + acceptance criteria and the api-spec operations + error model are the coverage checklist. Research to ground the plan in established test-strategy practice (ISTQB/IEEE-829 test levels and test-plan structure, risk-based testing, coverage-by-behavior). Then fill each section to method: scope and objectives; the test levels and types the project warrants; a coverage matrix mapping every behavior/operation/error to a level; environments and test data; testable entry/exit ("done") criteria; risk-based prioritization; and the test-case catalog (per case: id, preconditions, steps, expected result, traceability). Size the catalog by risk-weighted coverage — at least one case per behavior/error, more cases on high-risk/high-impact areas, fewer on trivial ones, not the full permutation cross-product. Pull performance/security/load levels from the NFRs where handed in. Surface a coverage gap (an untestable requirement, a missing NFR) as an explicit assumption rather than fabricate a behavior. Self-check against the coverage/testability bar before handoff.

## Output

A comprehensive test plan meeting the **coverage/testability bar** (every behavior in the handed-in upstreams has at least one traceable test case; the test levels fit the project; entry/exit criteria are testable; environments and test data are specified; each catalog case has preconditions + steps + expected result + traceability; the plan is risk-prioritized; the catalog is risk-weighted, neither thin nor combinatorial; nothing fabricated). Textual markdown — the method and bar are medium-independent. Structure from the template; this skill supplies the content quality. The same bar a runtime `reviewing-test-plan` gate asserts.

## Key guarantees

- **Composes, not duplicates** — defers structure to the template tool; supplies method + judgment.
- **Complete coverage, traced** — every upstream behavior/operation/error has at least one case that traces back to it.
- **Risk-weighted catalog** — depth scales by risk, not by input cross-product; a large product stays proportional, not combinatorial.
- **Testable done-criteria** — entry/exit criteria are mechanically evaluable, not "looks stable".
- **Specs cases, not scripts; never fabricated** — defines the cases; surfaces gaps as assumptions; never invents a behavior.
- **Single-sourced bar** — shared with `reviewing-test-plan` via the pair dossier, so produce and review don't drift.

## License

MIT © 2026 Bhushan Modi.
