# Design method — sections 1–6 (trace, decomposition, flow, interfaces, detailed design)

Depth for the SKILL.md Step-4 method, sections 1–6. Load when filling a TDD's
problem/trace/approach/flow/interface/detailed-design sections.

## Requirement traceability (RTM) — bidirectional

A TDD's spine. Build the trace as a small matrix and keep it honest in both
directions:

- **Forward (no coverage gap):** every requirement the feature must satisfy —
  each PRD goal / feature-spec acceptance criterion / hard constraint — has at
  least one design element that satisfies it. A requirement with no design is
  a coverage gap.
- **Backward (no orphan / no scope creep):** every non-trivial design decision
  cites the requirement behind it. A decision with no requirement is gold-
  plating — cut it or surface the missing requirement.
- **Form:** `Req ID | Requirement | Source` in section 2; then design sections
  reference the Req IDs ("§3 `ExportJob` satisfies R2"). On amend, re-check the
  trace for the changed decisions only.

## Altitude — design the feature, not the system (a C4 framing)

A TDD is **one level down** from the architecture-doc. Borrowing C4's levels:
the architecture-doc owns the Context/Container view (services, datastores,
topology); the TDD owns the Component view *for one feature* and references the
levels above. Tests for "am I at the wrong altitude":

- Re-deciding the datastore, the service boundaries, or a cross-cutting
  platform choice → architecture work; reference the architecture-doc instead.
- Designing how *one* feature's components collaborate within those given
  boundaries → correct TDD altitude.

## Component decomposition — single responsibility

- Start with a ≤2-paragraph **overview** of the chosen approach before any
  component detail (a reader should grasp the shape before the mechanism).
- Decompose into components/modules, each with **one responsibility** and its
  collaborators. A "Manager that handles everything" is a smell — split it.
- Position each against the existing system by **reference** ("reads via the
  existing `ReportQuery` port — architecture-doc §Reporting"), not by redrawing
  the surrounding structure.
- Bar: an engineer can map each component to code to write; responsibilities
  don't ambiguously overlap.

## Control + data flow — synced diagram + narration

- Render the **primary runtime (success) path** as a diagram: a **sequence
  diagram** for message exchange between components, a **flowchart** for a
  decision/data flow. Failures go in section 7, not here.
- Pair the diagram with a **numbered narration** — and keep them in sync: every
  step in the prose appears in the diagram and vice versa. Diagram/prose drift
  is the most common review finding here.
- In markdown the diagram is Mermaid (`sequenceDiagram` / `flowchart`).

## Key interfaces + contracts — the delta only (reference-not-duplicate / SSOT)

The signature TDD discipline. A fact has exactly one authoritative home;
copies drift the moment the source changes.

- Give the **signatures / message shapes / events / state** the feature
  **introduces or changes**, expressed as the *contract* (types, pre/post-
  conditions), not the final implementation. Fenced pseudo-signatures.
- For anything an **api-spec / data-model / architecture-doc already owns**:
  **reference it and state only the delta** ("reuses `GET /reports/{id}/rows`
  (api-spec §Reports); adds only `format=csv`"). Never inline the endpoint
  list, the table DDL, or the topology.
- Why: inlining a contract another doc owns guarantees drift; the reference +
  delta keeps a single source of truth. (RTM guidance: references are unique,
  replicated only when a design element genuinely resolves multiple
  requirements.)

## Detailed design — only the load-bearing logic

- Spend prose ONLY on the **non-obvious, load-bearing** logic: the core
  algorithm(s), the state the feature holds and its transitions, the tricky
  invariant, and any **concurrency / ordering / idempotency** concern (name the
  stance — safe-to-retry? at-least-once vs exactly-once? — or N/A).
- Express algorithms as fenced **pseudo-code** (the algorithm shape / the
  contract), not finished code.
- Trivial CRUD needs no prose — proportionality. The bar is "an implementer
  can't trivially derive this", not "every line is documented".
