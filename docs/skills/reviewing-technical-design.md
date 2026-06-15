# reviewing-technical-design

Judge a **finished technical-design document** (a TDD / engineering design doc / design RFC for one feature or component) and decide whether an engineer can implement it without re-deriving the design — an acceptance gate, not authoring. The review half of the technical-design pair, one layer below the feature-spec; it single-sources its bar from the same conditions as `authoring-technical-design`, so a TDD that passes is exactly one the author was aiming for.

## Purpose

A TDD says *how one feature will be built* within an existing system. Before an engineer implements from it, something has to decide whether the design is settled enough to build from — or whether the builder will have to re-derive decisions, invent failure handling, or chase an inlined contract that drifts. This skill is that gate: it judges a TDD against an **implementability bar** and emits a machine-parseable verdict, so produce → review → accept can run as a loop. The author's *techniques* (FMEA, the RTM trace matrix, C4 altitude, the diagram choice) are judged by **outcome**, never demanded — but rollout/observability/testing are real load-bearing conditions, not "invented" ones.

## When to activate

- ✅ A finished TDD needs an accept/revise decision before an engineer implements from it.
- ✅ You are the independent reviewer / gate for a TDD a producer just authored.
- ✅ Re-judging a revised TDD after a prior `revise`, or reviewing an **amend** as a delta-scoped review.

### When NOT to activate

- **Authoring or repairing a TDD** → `authoring-technical-design` (the producer revises on the findings).
- **Reviewing the upstream PRD or feature-spec** (what/why; how each feature behaves) → a PRD-review / feature-spec-review skill, one layer up.
- **Reviewing the api-spec or data-model themselves** → those are their own documents this TDD references, with their own gates.
- **A generic / ad-hoc engineering design doc, RFC, ADR, spec, or plan** → `design-review`. This gate is for the doc-library technical-design artifact (authoritatively the `template: technical-design` frontmatter; a `# Technical Design:` heading is a fallback only when frontmatter is absent).
- **Template/section conformance** → a template concern; this judges quality against the bar.

## The bar (11 conditions)

Judges each, pass/gap, proportional to the feature: (1) **requirement trace** complete + bidirectional (no orphan decision, no uncovered requirement); (2) **scoped to one feature** at the right altitude (system structure referenced, not redesigned); (3) **approach + decomposition implementable** (one responsibility per component, a diagram AND a numbered narration that agree); (4) **reference-not-duplicate (SSOT)** — contracts an api-spec/data-model/architecture-doc owns are referenced, not inlined; (5) **≥1 real alternative** with a stated decision criterion (no strawman, no rubber-stamp); (6) **failure modes + cross-cutting robustness** — each significant failure with detection + handling + user-visible effect; (7) **observability addressed** — the health/failure signals named (arming the rollback triggers); (8) **testing addressed** — levels + the cond-6 failure cases + contract conformance; (9) **rollout / migration / rollback** with measurable triggers; (10) **assumptions explicit + grounded, nothing fabricated**; (11) **(amend only) delta well-scoped, ripple-clean, versioned** (n/a greenfield). A thin feature legitimately collapses what it doesn't need; judge completeness-of-decisions, not word count.

## Output

Exactly `VERDICT: approve` or `VERDICT: revise` on its own line, plus findings. On `revise`, every finding is **actionable** — the failed condition, the exact location, and **how to fix it** — so the author resolves it in one pass. On `approve`, findings are optional non-blocking notes. **Approves** a TDD an engineer can build from (no false-revise on a thin one); **revises** only on a real, named implementability gap.

## Key guarantees

- **Gate, not author** — judges and returns findings; never rewrites or fills in the design.
- **Single-sourced bar** — the same 11 conditions the author produces to; no private stricter standard.
- **Aids judged by outcome, never demanded** — FMEA/RTM/C4/diagram-choice are techniques; a traced decision / a handled failure / a named signal are the conditions.
- **Reference-not-duplicate is load-bearing** — an inlined contract another doc owns is a real gap (drift), not a style nit.
- **No false-revise** — a thin feature's short TDD that meets every applicable condition is approved.
- **Machine-parseable verdict** — the exact `VERDICT:` line a loop can read.

## License

MIT © 2026 Bhushan Modi.
