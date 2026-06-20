# reviewing-architecture-doc

Judge a **finished whole-system architecture document (+ its linked ADR files)** and decide whether an engineer can grasp the system and place a feature's technical-design within it — an acceptance gate, not authoring. The review half of the architecture-doc pair, one altitude above the per-feature TDD; it single-sources its bar from the same conditions as `authoring-architecture-doc`. It judges **two artifacts**: the architecture doc AND its linked ADR files.

## Purpose

An architecture doc says how the whole system is structured and *why* its major decisions were made. Before engineers build within it, something has to decide whether a new reader can grasp the structure, follow the rationale, and locate a feature's design inside it without asking the author. This skill is that gate: it judges the doc + its ADRs against an **architecture-quality bar** and emits a machine-parseable verdict. Condition 4 (the ADR mechanism) is unverifiable from the doc alone — the reviewer needs the linked ADR files; if absent, it flags cond-4 unverifiable rather than fabricating. The author's *techniques* (C4, arc42, ATAM, 4+1, the diagram form) are judged by **outcome** — but the ADR mechanism, NFR-realization, and the system observability stance are real load-bearing conditions.

## When to activate

- ✅ A finished architecture doc needs an accept/revise decision before engineers build within it (or before a feature's TDD is placed within it).
- ✅ You are the independent reviewer / gate for an architecture doc a producer just authored.
- ✅ Re-judging a revised doc after a prior `revise`, or reviewing an **amend** as a delta-scoped review.

### When NOT to activate

- **Authoring or repairing an architecture doc** → `authoring-architecture-doc`.
- **Reviewing the upstream PRD / product direction** (what/why, the NFR targets) → a PRD-review skill, one layer up.
- **Reviewing one feature's technical-design** → `reviewing-technical-design`, one altitude lower.
- **Reviewing the api-spec or data-model themselves** → their own documents, with their own gates.
- **A generic / ad-hoc design doc, RFC, standalone ADR, spec, or plan** → `design-review`. This gate is for the doc-library architecture-doc artifact (authoritatively the `template: architecture-doc` frontmatter; a `# Architecture:` heading is a fallback only when frontmatter is absent; a standalone ADR not part of an architecture-doc stays with `design-review`).
- **Template/section conformance** → a template concern.

## The bar (11 conditions)

Judges each, pass/gap, proportional to the system: (1) **context, boundary + concerns** — what the system is/isn't responsible for, every actor + external dependency, a context diagram agreeing with the prose; (2) **structure + altitude** — every component named once with one responsibility, topology with direction/protocol per edge, stays at whole-system altitude (not endpoint/table/feature detail); (3) **diagrams ⇄ narrative in sync** + a deployment view where load-bearing; (4) **the ADR mechanism** (signature) — every significant decision a standalone LINKED ADR (one per file), index ⇄ files in sync, no accepted ADR rewritten; (5) **significant decisions traced + justified** — each names a driver + a real alternative; (6) **NFR realization + tradeoffs** — every target has a realizing mechanism (measurable for load-bearing), tensions named; (7) **cross-cutting concerns** — resilience per integration boundary, security, privacy, a system-level observability strategy; (8) **requirements / ASR coverage** — no uncovered ASR, no orphan structure; (9) **assumptions explicit + grounded, claims consistent with the real system** (`file:line`; greenfield clause — N/A when no code exists); (10) **(amend only) delta well-scoped, ripple-clean, versioned** (n/a greenfield). C4/arc42/ATAM/4+1 are aids judged by outcome.

## Output

Exactly `VERDICT: approve` or `VERDICT: revise` on its own line, plus findings. On `revise`, every finding is **actionable** — the failed condition, the exact location, and **how to fix it**. On `approve`, findings are optional non-blocking notes. **Approves** a doc a reader can grasp + place a feature within (no false-revise on a thin one); **revises** only on a real, named gap.

## Key guarantees

- **Gate, not author** — judges and returns findings; never rewrites the doc.
- **Single-sourced bar** — the same 11 conditions the author produces to; no private stricter standard.
- **Judges two artifacts** — the architecture doc AND its linked ADR files; cond-4 flagged unverifiable if the ADRs weren't handed in (never fabricated).
- **The ADR mechanism is load-bearing** — an inline-embedded decision or a rewritten accepted ADR is a real gap (un-addressable / destroyed history), the gap generic `design-review` misses.
- **Verifies claims against the system, with the greenfield clause** — consistency is N/A (never a blocker) when there's no code to verify against.
- **No false-revise** — a thin system's short doc that meets every applicable condition is approved.
- **capability-record-aware** — when capability records are injected by the authoring caller, judgment includes a capability-coverage condition (all active capabilities as components, `depends_on` DAG reflected); n/a when no records were injected.
- **Machine-parseable verdict** — the exact `VERDICT:` line a loop can read.

## License

MIT © 2026 Bhushan Modi.
