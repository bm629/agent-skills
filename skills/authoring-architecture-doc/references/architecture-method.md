# architecture-method — depth for authoring-architecture-doc

The per-section depth the SKILL.md body defers here. Load when filling a section to the production-grade bar. The body carries the method in one line per angle; this file carries the how.

## Context, boundary & concerns (§1)

- **Boundary first.** Draw in-scope / explicitly-out (+ who owns the out-of-scope) / actors / external dependencies (each with a one-line note on what it provides) before any component. An unnamed external is a hidden failure surface (it has no resilience stance — see resilience below).
- **System-context diagram (C4).** The system as one box among its external actors/systems; it must agree with the prose (diagram⇄narrative sync).
- **Stakeholders + concerns (ISO/IEC/IEEE 42010).** Identify the stakeholders and the concern each brings; the coverage rule is that **every named concern is framed by ≥1 later section/view**. This is the completeness yardstick — it lets the doc be checked against a concern set rather than by feel. Proportional: a thin product has few stakeholders/concerns.

## Structure, topology & views (§2–§3)

- **One responsibility per component.** Each major component named once with its single responsibility + kind (service/store/client/worker/queue). Review heuristic: a top level of ≤ ~7 coherent, loosely-coupled components — a smell-threshold, not a hard count. Each description precise enough for independent construction.
- **Topology: direction + protocol per edge.** Who talks to whom, in which direction, over which style (sync request/response vs async event/message). The container view maps closely to deployment.
- **Diagram⇄narrative sync.** Every box/arrow appears in the prose and vice-versa; diagrams read standalone (title + legend). Drift is a defect.
- **Runtime / deployment views where load-bearing.** A sequence/runtime view for non-obvious or concurrent flows (the 4+1 process view); a deployment view for a multi-node/multi-env system. Not every flow — the load-bearing ones.
- **Altitude.** Name major interfaces + data stores structurally; do NOT enumerate every endpoint (api-spec) or table (data-model), and do not slip into one feature's implementation (TDD).

## Integration boundaries (§4)

Per seam: what crosses it (link the api-spec/data-model, don't inline the schema), the communication style, who owns the contract + how it versions, and the failure stance when the far side is slow/down (→ resilience).

## The ADR mechanism (§7) — the signature discipline

- **Significance test:** record a decision as an ADR when it is **pervasive/foundational and costly to change** (runtime, datastore, messaging, hosting, trust model). Library-level picks are not significant.
- **Standalone, linked, one-per-file.** Each significant decision is its OWN ADR file (Nygard shape: Status / Context / Decision / Consequences, ~1–2 pages); the architecture doc carries a linked decisions INDEX, never an inline-embedded full record.
- **Trace + a real alternative.** Each decision names its driver (a requirement/NFR/ASR) and a genuine (non-strawman) alternative with the trade-off it lost on.
- **Immutable once accepted.** A changed decision is a NEW ADR that supersedes the old (old Status → "superseded by NNNN"); you do not rewrite an accepted record. (See `amend.md`.)
- **Index ⇄ files in sync.** Every indexed decision has a live ADR link; every accepted ADR appears in the index; superseded entries marked.

## NFR realization (§6)

- **Mechanism per target.** The PRD owns the targets; the architecture documents the realizing mechanism for each relevant pillar (scalability/availability/security/observability/deployment/cost). A restated target with no mechanism is a gap; a mechanism with no target is over-engineering.
- **Measurable quality-attribute scenarios.** For a load-bearing target, render it as a 6-part scenario (source / stimulus / artifact / environment / response / **response-measure**); the response-measure ("p99 < 200ms at 1000 rps") is the testable constraint.
- **Tradeoffs / sensitivity points (ATAM).** Where two attributes conflict (latency vs consistency, cost vs availability), state the tradeoff + which way it was resolved + why.

## Cross-cutting concerns (§6)

- **Resilience per boundary.** timeout / retry-with-backoff / circuit-breaker / fallback / graceful-degradation / bulkhead; cascading-failure containment — at system altitude.
- **Security architecture.** Trust boundaries, authn/authz approach, secrets handling, the untrusted-input surface, data in transit/at rest.
- **Data & privacy.** Classification, retention, residency where sensitive data flows.
- **Observability (system-level).** The golden signals + health/SLO-monitoring strategy that makes the SYSTEM operable — distinct from one feature's signals.
