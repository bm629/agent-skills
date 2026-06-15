# reviewing-test-plan

Judge a **finished test plan** and decide whether a tester can execute it and every behavior is covered — an acceptance gate, not authoring. The review half of the test-plan pair; single-sources its bar from the same dossier as `authoring-test-plan`.

## Purpose

The test plan is the QA/verification strategy plus the concrete test-case catalog a tester runs to verify a system's behavior. This skill is the gate that decides whether it's good enough: it judges the plan against a **coverage + testability bar** and emits a machine-parseable verdict, so produce -> review -> accept can run as a loop.

## When to activate

- Judging a finished/draft test plan before it's accepted.
- The review step of a produce->review->accept document loop.

### When NOT to activate

- **Authoring a test plan** -> `authoring-test-plan` (the producer revises on findings).
- **The release runbook** -> `reviewing-release-runbook`.
- **Judging or running the test automation code** -> the executable scripts are out of scope; this judges the plan document.
- **Engineering design docs** (ADR/RFC) -> `design-review`.

## The coverage + testability bar (10 conditions)

Judges each, pass/gap: every behavior in the **handed-in upstreams** (feature-spec behaviors + api-spec operations/errors, else the PRD) has **at least one traceable test case** — the reviewer enumerates behaviors from whatever upstream was handed in; the **functional test levels** fit the project; **entry/exit criteria are testable** (a coverage floor + an open-defect threshold), not vague; **environments + test data are specified**; **each catalog case has preconditions + steps + an observable expected result + traceability** (a metric-threshold on a named dataset for an ML/probabilistic case); the plan is **risk-prioritized** and the **catalog is risk-weighted** — a coverage gap, a padded/thin catalog, OR a combinatorial blow-up is a finding; **nothing is fabricated** (each case traces to a real upstream, spot-checked); each **warranted non-functional type carries a numeric/standard target** (perf load profile + p95, a threat-derived security set, WCAG 2.2 AA accessibility, a compatibility matrix, i18n) — a thin project warranting none is not a gap; and an **amend** is reviewed **delta-scoped** (re-traced coverage + impact/risk-selected regression set + version/changelog), never a full re-review — n/a on a greenfield build. Single-sourced from the shared dossier so the produce-bar and review-bar match.

## Output

Exactly `VERDICT: approve|revise` plus **actionable** findings (the failed condition + how to fix). **Approves** a proportionally-sized plan that meets the bar — no false-revise — and **revises** only on a real, named gap (e.g. a behavior with no test case, an untestable exit criterion, a permutation blow-up).

## Key guarantees

- **Gate, not author** — judges and returns findings; never writes the plan.
- **Single-sourced bar** — same conditions the author produces to; no drift.
- **Coverage is load-bearing** — a behavior in the upstreams with no traceable case is always a finding.
- **Risk-weighting is checked both ways** — both a coverage gap and a combinatorial blow-up are findings.
- **Delta-scoped amend** — a change request against an existing plan is judged on its re-traced coverage + impact/risk-selected regression set + version/changelog, never re-litigated as a full review.
- **No false-revise** — approves a proportionally-sized, fully-covering plan even if stylistically improvable; never demands a non-functional type the archetype doesn't warrant.
- **Machine-parseable verdict** — the exact `VERDICT:` line a loop can read.

## License

MIT © 2026 Bhushan Modi.
