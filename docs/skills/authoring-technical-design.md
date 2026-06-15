# authoring-technical-design

Author a **technical design document (TDD)** — the detailed implementation design for building **one feature or component** within an existing system: the chosen approach, the component decomposition, the control + data flow, the key interfaces, the significant logic, the failure modes, the alternatives weighed, the testing, and the rollout. The how-to (a design-research method + an implementability bar), composed with a separate technical-design template tool and a deep-research capability; targets a textual markdown artifact (prose + Mermaid sequence/flow + fenced interface/pseudo-code + a trade-off table).

## Purpose

The PRD says *what* the product does and the feature-spec says *how each feature behaves*; the TDD says *how this feature will be built*. This skill carries the producer's judgment — not the section list — guiding a producer to ground the design in established design-doc practice and the project's real constraints, trace every decision to a requirement, compare at least one real (non-strawman) alternative with a stated decision criterion, reference the architecture-doc / API spec / data-model rather than duplicating them, and address failure modes, testing, and rollout. The bar to clear: an engineer can implement the feature from the doc without re-deriving the design, and the chosen approach is justified against at least one real alternative.

## When to activate

- Authoring a TDD for one feature-spec'd feature/component, designing how it will be built within the existing system.
- Deciding and documenting the implementation approach: component decomposition, control/data flow, interfaces, detailed logic, failure modes, observability, testing, and rollout.
- **Amending an approved TDD** as a versioned, ripple-analyzed delta (a chosen approach proves unworkable mid-build, a feature-spec behavior is corrected, a new failure mode appears).
- Filling a technical-design template with researched, decision-complete content traced to the feature's requirements.

### When NOT to activate

- **Whole-system structure / service topology / long-lived tech choices** → `authoring-architecture-doc` (higher altitude; the TDD designs one feature *within* it and references it).
- **The API contract or the data schema** → `authoring-api-spec` / `authoring-data-model` (the TDD *references* those, never duplicates them).
- **The PRD or the feature-spec** → those are *upstream input* here.
- **Reviewing a finished TDD** → `reviewing-technical-design` (its dedicated reviewer; the generic `design-review` gates its engineering siblings — RFCs/ADRs/specs/plans — not this artifact).

## Workflow

Take the section structure from the technical-design template tool (don't invent an outline). Load the approved PRD + feature-spec (and the architecture-doc / API spec / data-model where present) — the feature-spec's requirements are the coverage checklist; every design decision traces back to one. Research to ground the design in established design-doc practice and the project's actual constraints. Then fill each section to method: context + requirement trace; chosen approach + a one-responsibility-per-component decomposition; control + data flow as a synced diagram + narration; key interfaces/contracts (referencing the owning api-spec/data-model, stating only the delta); the non-obvious detailed logic; error handling with each failure's detection + recovery; the cross-cutting concerns (security/privacy + **observability** as a first-class signal set that arms the rollback triggers); at least one real alternative with the decision criterion that settled it; the testing approach; and rollout/migration + a rollback with measurable triggers. Self-check against the 11-point implementability bar before handoff; surface unknowns as explicit assumptions, never silent defaults. On an **amend** (an approved TDD + a change request), edit the affected decision(s) in place — re-make the internal chain, analyze the bidirectional + SSOT ripple, version + changelog, mark superseded decisions — never regenerate the whole doc.

## Output

A comprehensive technical design document meeting the **implementability bar** (every decision traced to a requirement, an implementable approach + decomposition, control/data flow as a synced diagram + narration, interfaces/data referencing their owning docs, failure modes + observability + testing + rollout/rollback addressed, at least one real alternative with a decision criterion, assumptions explicit, scoped to one feature; on amendment, a scoped versioned delta). Textual markdown — the method and bar are medium-independent. Structure from the template; this skill supplies the content quality. The same 11-condition bar the `reviewing-technical-design` gate asserts, so author and reviewer don't drift.

## Key guarantees

- **Composes, not duplicates** — defers structure to the template tool; supplies method + judgment.
- **References, never inlines** — interfaces/schemas/system-structure owned by an api-spec/data-model/architecture-doc are referenced with only the delta, so the TDD can't drift from the source of truth.
- **Feature altitude** — designs one feature within the architecture; system-wide structure is referenced, not redesigned.
- **Justified, not rubber-stamped** — at least one real alternative with a decision criterion; failure modes carry their handling; observability + a measurable-trigger rollback addressed.
- **Amends in place** — on a change to an approved TDD, edits the affected decisions + versions + analyzes the ripple; never regenerates.
- **Single-sourced bar** — shared with the `reviewing-technical-design` gate, so produce and review don't drift.

## License

MIT © 2026 Bhushan Modi.
