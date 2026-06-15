# reviewing-feature-spec

Judge a **finished feature specification** and decide whether engineering can plan and build from it — an acceptance gate, not authoring. The review half of the feature-spec pair; single-sources its bar from the same dossier as `authoring-feature-spec`.

## Purpose

The feature spec is the layer below the PRD — it says how each feature behaves, in enough detail to build and test. This skill is the gate that decides whether it's good enough: it judges the spec against an **implementability + testability bar** and emits a machine-parseable verdict, so produce → review → accept can run as a loop.

## When to activate

- ✅ Judging a finished/draft feature spec before it's accepted for planning/build.
- ✅ The review step of a produce→review→accept document loop.

### When NOT to activate

- **Authoring a feature spec** → `authoring-feature-spec` (the producer revises on findings).
- **Reviewing the upstream PRD** → `reviewing-prd`.
- **Engineering design docs** (ADR/RFC) → `design-review`.

## The implementability + testability bar (10 conditions)

Judges each, pass/gap: every feature **traces** to a PRD need (no orphans, no coverage gaps); behavior **unambiguous + observable**; **inputs/outputs + states complete** (a state-transition table where stateful); every **edge case names its expected response**; **acceptance criteria independently testable** (Given/When/Then, or a metric-threshold on a named dataset for a probabilistic/ML feature); requirements singular + consistent; feasible + plannable; open questions surfaced; **load-bearing non-functional requirements carry numeric targets**; an **amend** reviewed delta-scoped (the change + its ripple, n/a on a greenfield first build). EARS, decision tables, and archetype overlays are authoring aids judged by outcome, never demanded. Single-sourced from the shared dossier so the produce-bar and review-bar match.

## Output

Exactly `VERDICT: approve|revise` plus **actionable** findings (the failed condition + how to fix). **Approves** a spec that meets the bar — no false-revise — and **revises** only on a real, named gap.

## Key guarantees

- **Gate, not author** — judges and returns findings; never writes the spec.
- **Single-sourced bar** — same conditions the author produces to; no drift.
- **No false-revise** — approves a buildable spec even if stylistically improvable.
- **Machine-parseable verdict** — the exact `VERDICT:` line a loop can read.

## License

MIT © 2026 Bhushan Modi.
