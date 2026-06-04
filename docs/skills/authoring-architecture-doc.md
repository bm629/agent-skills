# authoring-architecture-doc

Author a **software/system architecture document** — the whole-system structure: context and scope, the major components/services and their responsibilities, the interaction topology and integration boundaries, the significant technology choices and their rationale, and how the system realizes its non-functional/quality targets. The how-to (an architecture-research method + a usability bar + a decision-recording mechanism), composed with a separate architecture-doc template tool AND an ADR template tool, plus a deep-research capability; targets a textual markdown artifact (prose + Mermaid component/container/C4-style diagrams + a decisions-index table).

## Purpose

A new engineer needs to grasp the system's structure and the *why* of its major decisions, and a feature's technical-design needs somewhere to locate itself. This skill carries the producer's judgment — not the section list — guiding a producer to scope the boundary first, name a single responsibility per component, justify each significant tech choice, give every NFR target a realization, and record each key decision as a standalone, linked ADR file (the doc carries only a decisions index). The bar to clear: a new engineer grasps the structure and the major decisions, and a feature's technical-design can place itself within it.

## When to activate

- Authoring a new architecture doc for a system or product from an approved PRD.
- Expanding a thin product direction into a whole-system architecture (sized to the product).
- Filling an architecture-doc template with researched, decision-complete content, recording the key decisions as linked ADR files.

### When NOT to activate

- **One feature's implementation design** → `authoring-technical-design` (lower altitude; it references this doc).
- **The wire contract (every endpoint) or the persistence model (every table)** → `authoring-api-spec` / `authoring-data-model` (this doc names the major interfaces + data stores *structurally*, not exhaustively).
- **Reviewing a finished architecture doc** → a design-review gate.

## Workflow

Take the section structure from the architecture-doc template tool and the standalone decision-record shape from the ADR template tool (don't invent an outline). Load the approved PRD + product direction; fill knowledge gaps; commit to elaborating *this* product, not a generic fill. Research to ground each choice in established practice (e.g. C4, reference architectures, the actual stack). Then fill each section to method: boundary first (in/out, actors, external dependencies); one responsibility per component; protocol per arrow with the diagram + narrative in sync; failure semantics per integration boundary; a rationale (driver + what it beat) per significant tech choice; a realization mechanism per NFR target (the PRD owns the targets, the architecture owns the how). Record each significant decision as a standalone ADR file (one decision per file, traced to a driver with a real alternative, immutable once accepted — supersede rather than edit) and carry only a linked summary index in the doc. Self-check against the 9-point usability bar before handoff.

## Output

A whole-system architecture document meeting the **usability bar** (graspable structure; components + boundaries named with responsibilities; justified tech choices; a realization per NFR target; key decisions as standalone linked ADRs, indexed and in sync; diagram + narrative in sync; sized to the archetype; grounded-not-boilerplate), plus a set of standalone ADR files the doc's key-decisions index links. Textual markdown — the method and bar are medium-independent. Structure from the template tools; this skill supplies the content quality and the decision-recording mechanism. The same bar a runtime design-review gate asserts.

## Key guarantees

- **Composes, not duplicates** — defers structure to the template tools; supplies method + judgment.
- **Decisions linked, not embedded** — every significant decision is a standalone ADR file; the doc carries only a linked index, so each decision is independently addressable and the history stays append-only.
- **NFR targets realized, not restated** — every quality target the PRD names carries a mechanism that meets it.
- **Sized to the archetype** — covers the components/boundaries/NFRs the product actually needs, with no invented structure beyond that; kept at whole-system altitude.
- **Single-sourced bar** — shared with the runtime design-review gate (there is no dedicated architecture-doc reviewer; this skill's bar is that gate's checklist).

## License

MIT © 2026 Bhushan Modi.
