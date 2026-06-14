# Sources — `authoring-technical-design`

Research provenance for the design-research method and the implementability
bar. The skill body paraphrases these; nothing is copied verbatim. External
content was descriptive (section names, structural guidance) — no commands,
URLs, or tool references were lifted into actions.

## The design-doc / RFC genre and its section set

- **Malte Ubl, "Design Docs at Google"** (industrialempathy.com) — the
  canonical anatomy: Context and scope, Goals and non-goals (non-goals are
  deliberate exclusions, e.g. is ACID compliance a goal?), the actual design
  (system-context diagram, APIs, data storage, code/pseudo-code, degree of
  constraint), Alternatives considered (a fixed section, focused on
  trade-offs), and Cross-cutting concerns (security/privacy/observability).
  Also: design docs trend short, and detailed material is **linked, not
  inlined**.
- **The Pragmatic Engineer (Gergely Orosz)** — "Companies Using RFCs or
  Design Docs and Examples of These" and "Software Engineering RFC and Design
  Doc Examples and Templates": the common cross-company section set —
  problem/context, proposed solution, detailed design, alternatives, testing,
  rollout milestones, open questions, security; company practice (Uber's DUCK
  → RFC, etc.).
- **Squarespace RFC template** (Slab library) — goals/background through
  risks and dependencies.
- **Fuchsia RFC template** (fuchsia.dev) — detailed design, testing /
  conformance suites, security considerations, implementation/rollout
  milestones.
- **Engineering-design-doc templates** (Zoom gallery; Range "Better Tech
  Specs"; Assemble tech-design template) — design overview, component design,
  sequence diagrams + data flow, error handling, testing strategy.

## Diagrams (textual medium)

- **UML sequence-diagram and data-flow-diagram practice** (Gliffy; IBM "What
  Is a Data Flow Diagram"; Mural; ConceptDraw) — sequence diagrams show
  time-ordered object interactions; DFDs visualize data movement between
  processes/stores. Basis for "sequence diagram for message exchange,
  flowchart for decision/data flow", rendered as Mermaid in markdown.

## Reference-not-duplicate (single source of truth)

- **Speakeasy, "Documentation Best Practices in REST API Design"** — keep the
  spec as the source of truth; duplicating it across docs is the common
  failure where documentation and the API drift apart.
- **Google Cloud API Design Guide** + general API-design IA guidance —
  layered docs that reference the authoritative spec rather than recreating
  the reference; conceptual/architectural docs layer on top of the
  machine-honest reference.

## Failure modes, cross-cutting concerns, observability

- **Mike Cvet, "Goals and Failure Modes for RFCs and Technical Design
  Documents"** (Better Programming) — the failure-modes framing of a design
  doc; problem/goals/non-goals/alternatives/risks as the load-bearing set.
- **FMEA practice** (failure mode + effects analysis) — each failure carries
  its detection, its effect, and its mitigation; basis for the
  failure-mode-with-handling table.
- **Observability practice** (the three pillars — logs / metrics / traces;
  alerting on the dominant failure mode) — name the health/failure signals
  that detect the failure modes and arm the rollback triggers.

## Rollout, migration, rollback

- **Squarespace RFC** (rollout/timeline section, updated as the RFC progresses
  to rollout) and **RFC change-plan + rollback-support models** — phasing /
  feature-flag enablement and a documented revert with measurable triggers.
- **Feature-flag rollout practice** — phased/dark-launch enablement; the flag
  is the rollback lever.

## Amend / versioning lifecycle

- **RFC/ADR lifecycle practice** — RFC "Status: Superseded by NNN" + a
  reciprocal note; a status→date table for a fuller history; ADR
  proposed/accepted/deprecated/superseded states; IETF RFC updates/obsoletes
  conventions. Basis for amending an approved design as a versioned,
  changelogged delta that marks (not deletes) superseded decisions.

## Implementability bar (what makes a design good)

- **Design-validation practice** (Fahim ul Haq, "How the best engineers
  validate a design before implementation") — a repeatable validation
  checklist; validate explicit assumptions about traffic/data/usage.
- **Requirements / SRS quality guidance** (SRS document checklist; "How to
  Write Good Requirements") — a good requirement is feasible, complete, and
  **traceable** to its source; traceability is **bidirectional** (forward:
  requirement→design; backward: design→requirement); surface unstated
  assumptions rather than relying on them.
