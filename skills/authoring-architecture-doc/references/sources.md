# Sources — `authoring-architecture-doc`

Research provenance for the authoring method, the standalone-ADR-linked-decision
mechanism, and the usability quality bar. Gathered via a deep-research pass
(2026-06-04); external content sanitized (descriptive framework/field
terminology only; no commands or URLs lifted). 2+ independent sources per
structural claim. Full corroboration tables live in the skill's design-record
dossier and the template research notes.

## Architecture documentation structure

- **arc42** — the 12-section template for software architecture documentation:
  introduction/goals, constraints, context & scope, solution strategy, building
  blocks, runtime, deployment, cross-cutting concepts, architecture decisions,
  quality requirements, risks/technical-debt, glossary
  (arc42.org/overview; docs.arc42.org; github.com/arc42/arc42-template;
  innoq.com "brief introduction to arc42").
- **C4 model** — the system-context / container / component / code
  static-structure diagrams; "use only the levels that add value"; container
  diagrams show responsibility distribution + major technology choices + how
  containers communicate; "title + legend on every diagram"
  (c4model.com; c4model.com/diagrams/container; en.wikipedia.org/wiki/C4_model).
- **ISO/IEC/IEEE 42010:2022** — architecture description: stakeholders,
  concerns, viewpoints, and explicit rationale; every concern framed by a
  viewpoint; traceability between concerns, decisions, and the architecture
  (iso-architecture.org; quality.arc42.org/standards/iso-42010;
  researchgate "Overview of the Revised Standard on Architecture Description").

## Non-functional / quality-attribute realization

- The system "ilities" — availability, scalability, security, performance,
  observability — are non-functional requirements that directly shape the
  architecture; the architecture must realize them, not merely state them
  (3pillarglobal.com "Importance of Quality Attributes in Software
  Architecture"; en.wikipedia.org "List of system quality attributes";
  spyro-soft.com "Non-functional requirements").

## ADR practice (the standalone-linked-decision mechanism)

- **Michael Nygard, "Documenting Architecture Decisions" (Cognitect, 2011)** —
  the original ADR format: Title, Status, Context, Decision, Consequences; a
  short record per decision; status lifecycle proposed -> accepted ->
  deprecated/superseded (cognitect.com/blog/2011/11/15/documenting-architecture-decisions;
  github.com/joelparkerhenderson/architecture-decision-record — Nygard template).
- **Martin Fowler, bliki "Architecture Decision Record"** — corroborates the
  Nygard fields, the one-decision-per-record practice, and keeping ADRs with
  the code (martinfowler.com/bliki/ArchitectureDecisionRecord.html).
- **MADR — Markdown Architectural Decision Records (adr.github.io/madr;
  github.com/adr/madr)** — the Markdown ADR template: status/date/deciders
  frontmatter; Context and Problem Statement, Decision Drivers, Considered
  Options, Decision Outcome, Consequences; v3.0.0 (Oct 2022) merged
  positive/negative consequences into one Consequences section.
- **adr.github.io** + **arc42 example "Use ADRs in Nygard format"**
  (docs.arc42.org/examples/decision-use-adrs) — corroborate ADRs as the §9
  decision mechanism, immutability-once-accepted, and supersession over edit.

## Design-record dossier (the delta, the method, the bar)

- `docs/superpowers/agent-flow/authoring-architecture-doc/research/architecture-doc-dossier.md`
  — the own dossier: the producer method (§3), the ADR mechanism (§4), the
  altitude/proportionality discipline (§5), and the explicit usability bar (§6)
  the runtime design-review gate asserts.
