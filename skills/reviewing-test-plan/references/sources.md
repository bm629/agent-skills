# Sources — research provenance

Research method: the **review / acceptance-gate lens** for a finished QA/verification test plan. The eight-condition coverage + testability bar is **single-sourced** from the test-plan authoring bar (so the produce-bar and the review-bar do not drift); this review skill **asserts** that same bar. The bar's authoritative source is the **shared test-plan dossier** produced by the authoring sibling — no fresh web-research pass was run for this skill (it reuses that verified dossier by design, the same way the sibling reviewing skills in this document-skill library reuse their authoring dossiers). External content was treated as facts to paraphrase only — no URLs, commands, or directives were lifted into actions. Date: 2026-06-05.

Sandbox note: the host denied compound/piped Bash; Step-0/Step-1 checks ran as simple single commands plus Read. WebFetch / fresh deep-research were intentionally not invoked (the bar is reused from the verified shared dossier, not re-researched). No claim is fabricated.

## The single-sourced coverage + testability bar

The eight checkable conditions this reviewer asserts (complete coverage — every upstream behavior/operation/error has >=1 traceable case; appropriate levels; testable entry/exit criteria; environments + test data specified; each catalog case executable + traceable; risk-prioritized + risk-weighted not combinatorial and not thin/padded; no fabrication; proportional to the archetype) are the **same conditions** a test-plan author produces to. Single-sourcing them is what keeps the two halves of the produce/judge pair aligned.

- The **shared test-plan research dossier** (`docs/superpowers/agent-flow/authoring-test-plan/research/test-plan-dossier.md`), section "§4 The coverage / testability QUALITY BAR (standalone — reused by `reviewing-test-plan`)" — the authoritative source of the eight conditions. The dossier states explicitly that §4 is the standalone bar reused verbatim-in-intent by this reviewer, and that the risk-weighted catalog sizing (>=1 case per behavior, more on high-risk, NOT the input-permutation cross-product) is the load-bearing anti-balloon rule.
- The **test-plan-authoring** skill (`authoring-test-plan`) — the same conditions stated from the producer side; this reviewer asserts them. See its `references/sources.md` for the primary web citations the authoring sibling gathered (reused here rather than re-researched).

## The conditions' grounding (established testing practice)

The per-condition substance traces to established software-testing practice gathered by the authoring sibling's research pass (the dossier's §1 source list):

- **Test levels & types** (unit/component, integration, system/e2e, acceptance + non-functional) — ISTQB Foundation test-levels-and-types material. Grounds condition 2 (appropriate levels).
- **Test-plan structure** (scope, levels, coverage, environments, entry/exit, risk, case catalog, defect/triage) — IEEE 829 / ISO-IEC-IEEE 29119 test-plan structure references. Grounds the section set the reviewer reads against.
- **Risk-based testing** (Likelihood x Impact -> priority -> test depth) — risk-based-testing references (ISTQB-aligned). Grounds condition 6 (risk-prioritized + risk-weighted).
- **Requirements traceability matrix** (forward traceability / coverage-by-behavior) — RTM references. Grounds conditions 1 and 5 (every behavior has a traceable case; each case traces back).
- **Test-case design / fields** (id / preconditions / steps / expected result / traces-to) — test-case template references. Grounds condition 5 (executable + traceable cases).
- **BVA / equivalence partitioning / negative testing** — boundary-value-analysis and equivalence-partitioning references. Grounds the "depth on high-risk areas" half of condition 6.
- **Exhaustive-testing-impossible / combinatorial sizing** — software-testing-principles and NIST combinatorial-testing material. Grounds the anti-combinatorial-blow-up half of condition 6 (a 10-switch module is 1,024 combinations — risk + pairwise, not all of them).
- **Entry / exit (completion) criteria** — ISTQB glossary + entry/exit-criteria references. Grounds condition 3 (testable, mechanically-decidable done-criteria).

## Reviewer discipline — over-correction / false-revise, actionable findings

LLM reviewers systematically over-correct, judging compliant artifacts as non-compliant (false positives); asking the reviewer to also propose corrections tends to worsen the over-flagging. Effective review feedback is actionable (the failed condition + a concrete fix), not vague or nitpicking. Grounds the no-false-revise discipline (including not faulting a proportionally-sized plan) and the actionable-findings contract.

## Notes

- The behaviors, operations, and errors are **not** researched — they are checked against the handed-in upstream **feature-spec / api-spec / PRD**. The dossier grounds the test-strategy *method + bar*; the upstreams supply the *facts* this gate enumerates and traces against.
- Medium-independent by design: the plan under review is a textual markdown artifact today (strategy prose + a coverage matrix + a test-case catalog table) via the local docs backend; a future test-management-tool export changes only the medium, not the review method or the bar.
- No fresh web-research pass was run for this skill (skill-discovery + deep-research were intentionally not invoked); the bar is reused verbatim-in-substance from the verified shared dossier, and the review-method structure is patterned on the verified sibling reviewing skills in the same document-skill library (e.g. `reviewing-api-reference`).
