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

## The coverage + testability bar

Judges each, pass/gap: every behavior in the **handed-in upstreams** (feature-spec behaviors + api-spec operations/errors, else the PRD) has **at least one traceable test case** — the reviewer enumerates behaviors from whatever upstream was handed in; the **test levels** fit the project; **entry/exit criteria are testable**, not vague; **environments + test data are specified**; **each catalog case has preconditions + steps + expected result + traceability**; the plan is **risk-prioritized** and the **catalog is risk-weighted** — a coverage gap, a padded/thin catalog, OR a combinatorial blow-up is a finding; **nothing is fabricated** (each case traces to a real upstream, spot-checked). Single-sourced from the shared dossier so the produce-bar and review-bar match.

## Output

Exactly `VERDICT: approve|revise` plus **actionable** findings (the failed condition + how to fix). **Approves** a proportionally-sized plan that meets the bar — no false-revise — and **revises** only on a real, named gap (e.g. a behavior with no test case, an untestable exit criterion, a permutation blow-up).

## Key guarantees

- **Gate, not author** — judges and returns findings; never writes the plan.
- **Single-sourced bar** — same conditions the author produces to; no drift.
- **Coverage is load-bearing** — a behavior in the upstreams with no traceable case is always a finding.
- **Risk-weighting is checked both ways** — both a coverage gap and a combinatorial blow-up are findings.
- **No false-revise** — approves a proportionally-sized, fully-covering plan even if stylistically improvable.
- **Machine-parseable verdict** — the exact `VERDICT:` line a loop can read.

## License

MIT © 2026 Bhushan Modi.
