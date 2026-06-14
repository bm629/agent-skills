# Sources — `reviewing-architecture-doc`

Research provenance for the review method, the single-sourced architecture-quality
bar, and the ADR-mechanism / NFR-realization / verify-against-reality disciplines.
The bar is single-sourced 1:1 with `authoring-architecture-doc` Step-7 (the
produce-bar). External content sanitized (descriptive framework/field terminology
only; no commands or URLs lifted). 2+ independent sources per structural claim.

## Architecture documentation structure (what a reader needs)

- **arc42** — the 12-section architecture-documentation template (context & scope,
  building blocks, runtime, deployment, cross-cutting concepts, architecture
  decisions, quality requirements, risks) — the section coverage a complete doc
  has (arc42.org; docs.arc42.org).
- **C4 model** — system-context / container / component views; the altitude the
  doc holds (structural, not endpoint/table/feature detail) (c4model.com).
- **ISO/IEC/IEEE 42010:2022** — architecture description: stakeholders + concerns,
  every concern framed by ≥1 viewpoint/view — the coverage spine cond-1 checks
  (iso-architecture.org; quality.arc42.org/standards/iso-42010).

## The ADR mechanism (cond-4 — the signature condition)

- **Michael Nygard, "Documenting Architecture Decisions" (2011)** — the ADR format
  (Status/Context/Decision/Consequences), one decision per record, immutable once
  accepted, a changed decision is a NEW ADR that supersedes the old (old Status →
  "superseded by"); "small modular docs have a chance at being updated"
  (cognitect.com; github.com/joelparkerhenderson/architecture-decision-record).
- **adr.github.io / MADR / Martin Fowler bliki** — corroborate the
  one-decision-per-file, linked-index, supersede-not-edit practice.

## NFR realization + tradeoffs (cond-6)

- **SEI quality-attribute scenario** — source/stimulus/artifact/environment/
  response/**response-measure**; the response-measure is the testable constraint
  (sei.cmu.edu; socadk.github.io/design-practice-repository).
- **ATAM** — quality-attribute analysis yields risks/non-risks/sensitivity-points/
  tradeoff-points; tradeoffs are named + resolved (sei.cmu.edu ATAM report).

## Cross-cutting (cond-7) + verify-against-reality (cond-9)

- **Resilience patterns** — timeout/retry/circuit-breaker/fallback/degrade/bulkhead
  at integration boundaries (microservices resilience-pattern references).
- **Well-Architected pillars** — operational-excellence/security/reliability/
  performance/cost; the system observability posture (AWS/Azure references).
- **Consistency-with-the-shipped-system** — verify claims about what the system IS
  against the real code/topology (`file:line`); the discipline inherited from the
  generic `design-review` Step-4, with its greenfield-N/A clause.

## Review-gate contract

- Single-sourced with the author (one bar, no drift); proportional (no false-revise
  on a thin doc); aids judged by outcome (C4/arc42/ATAM/4+1 are techniques, not
  conditions); delta-scoped amend; emits the literal `VERDICT: approve|revise`.
  Adapted from the canonical sibling `reviewing-technical-design`.
