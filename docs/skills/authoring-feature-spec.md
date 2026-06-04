# authoring-feature-spec

Author a **feature specification** — the layer below the PRD that elaborates each named feature into implementable, testable detail. The how-to (method + testability bar), composed with a separate feature-spec template tool; assumes the approved PRD as upstream input, never a blank page.

## Purpose

A PRD names *what* features to build; engineers and testers need *how each one behaves*, in enough detail to build and verify without asking the author. This skill guides a producer to elaborate the PRD's features into a comprehensive, testable feature spec — tracing each feature to a PRD goal, specifying observable behavior, enumerating inputs/outputs and states, covering edge cases with their expected handling, and writing testable Given/When/Then acceptance criteria.

## When to activate

- ✅ Authoring a feature spec from an approved PRD.
- ✅ The produce step for the feature-spec document in a produce→review→accept loop.

### When NOT to activate

- **Authoring the PRD itself** → `authoring-prd` (it's upstream).
- **Reviewing a finished feature spec** → `reviewing-feature-spec`.
- **Engineering design docs** (ADR/RFC) → `design-review` family.

## Workflow

Take the structure from the feature-spec template tool (don't invent an outline). Drive coverage off the PRD's feature list. Per feature: (1) **trace** it to a PRD goal/need; (2) specify **observable, implementation-free behavior**; (3) enumerate **inputs/outputs + data** and valid/invalid boundaries; (4) **states + transitions** (collapse if stateless); (5) **edge cases each with their expected handling** (null/empty, duplicate/idempotency, concurrency, permissions, limits); (6) **testable acceptance criteria** (Given/When/Then or rule-based). Where the PRD is thin, surface an explicit open question or stated assumption — never silently invent.

## Output

A comprehensive feature spec meeting the **implementability + testability bar** (every feature traced, behavior unambiguous, I/O + states complete, edge cases covered with handling, acceptance criteria testable) — the same bar `reviewing-feature-spec` asserts. Structure from the template; this skill supplies the content quality.

## Key guarantees

- **Composes, not duplicates** — defers structure to the template tool; supplies method + judgment.
- **PRD is upstream input** — elaborates named features; never a blank page.
- **Testable by construction** — edge cases carry handling; acceptance criteria are independently verifiable.
- **Single-sourced bar** — shared with the reviewer, so produce and review don't drift.

## License

MIT © 2026 Bhushan Modi.
