# reviewing-prd

Judge a **finished PRD** and decide whether the downstream build can be planned from it — an acceptance gate, not authoring. The review half of the PRD pair; it single-sources its bar from the same research as `authoring-prd`, so a PRD that passes is exactly one the author was aiming for.

## Purpose

A PRD is the keystone product document — planning derives features, the MVP cut, and milestones from it. Before that happens, something has to decide whether the PRD is *good enough to plan from*. This skill is that gate: it judges a PRD against a **plannability bar** and emits a machine-parseable verdict, so produce → review → accept can run as a loop.

## When to activate

- ✅ Judging a finished/draft PRD before it's accepted as the basis for planning.
- ✅ The review step of a produce→review→accept document loop.

### When NOT to activate

- **Authoring or fixing a PRD** → `authoring-prd` (the producer revises on the findings).
- **Reviewing an engineering design doc** (spec, ADR, RFC) → `design-review`.
- **Other document types** → their own reviewing skill.

## The plannability bar (13 conditions)

Judges each, pass/gap: (1) problem **evidenced**, not asserted; (2) users/personas concrete; (3) **measurable** success metrics (target + method, plus guardrails where a headline metric is obviously gameable); (4) explicit, **defensible MVP boundary** (in/out + non-goals + release criteria); (5) feature set + acceptance criteria concrete enough to derive milestones; (6) **no fabricated evidence** (blocking); (7) risks/dependencies-context + open questions surfaced; (8) clear and unambiguous; (9) **non-functional requirements carry numeric targets**; (10) **traceable — no orphans** (every feature serves a goal, every goal has a feature); (11) **dependencies named**; (12) an **amend** reviewed delta-scoped (the change + its ripple, not a full re-review). Conditions 9–12 collapse proportionally on a thin PRD, so a small complete PRD is never false-revised. The bar is single-sourced from the PRD-authorship dossier so the produce-bar and review-bar match.

## Output

Exactly `VERDICT: approve|revise` plus **actionable** findings (the failed condition + location + how to fix). **Approves** a PRD that meets the bar — no false-revise — and **revises** only on a real, named gap. Plannability, not perfection.

## Key guarantees

- **Gate, not author** — judges and returns findings; never writes the PRD.
- **Single-sourced bar** — same conditions the author produces to; no private stricter standard, no drift.
- **No false-revise** — approves a PRD that is plannable even if stylistically improvable.
- **capability-record-aware** — when capability records are injected by the authoring caller, judgment includes a capability-coverage condition (all active L1 areas as named scope sections); n/a when no records were injected.
- **Machine-parseable verdict** — the exact `VERDICT:` line a loop can read.

## License

MIT © 2026 Bhushan Modi.
