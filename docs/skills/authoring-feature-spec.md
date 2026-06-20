# authoring-feature-spec

Author a **feature specification** — the layer below the PRD that elaborates each named feature into implementable, testable detail. The how-to (method + testability bar), composed with a separate feature-spec template tool; assumes the approved PRD as upstream input, never a blank page.

## Purpose

A PRD names *what* features to build; engineers and testers need *how each one behaves*, in enough detail to build and verify without asking the author. This skill guides a producer to elaborate the PRD's features into a comprehensive, testable feature spec — tracing each feature to a PRD goal, specifying observable behavior, enumerating inputs/outputs and states, covering edge cases with their expected handling, and writing testable Given/When/Then acceptance criteria.

## When to activate

- ✅ Authoring a feature spec from an approved PRD.
- ✅ **Amending** an approved feature spec as a versioned, ripple-analyzed delta (a feature/behavior/AC/state changed or added).
- ✅ The produce step for the feature-spec document in a produce→review→accept loop.

### When NOT to activate

- **Authoring the PRD itself** → `authoring-prd` (it's upstream).
- **Reviewing a finished feature spec** → `reviewing-feature-spec`.
- **Engineering design docs** (ADR/RFC) → `design-review` family.

## Workflow

Take the structure from the feature-spec template tool (don't invent an outline). Drive coverage off the PRD's feature list; name each feature's **archetype** (UI/API/data-ML/batch/integration/CLI), which shifts the emphasis. Per feature: (1) **trace** it to a PRD goal/need; (2) specify **observable, implementation-free behavior** — prefer **EARS** phrasing and classify flows (main/alternate/exception); a combinatorial rule gets a **decision table**; (3) enumerate **inputs/outputs + data** and valid/invalid boundaries; (4) **states + transitions** as a state-transition table (collapse if stateless); (5) **edge cases each with their expected handling** (null/empty, duplicate/idempotency, concurrency, permissions, limits); (6) **testable acceptance criteria** (Given/When/Then or rule-based — or **metric-threshold on a named dataset** for a probabilistic/ML feature); (7) the applicable **non-functional-requirement** targets, proportional to the archetype. Where the PRD is thin, surface an explicit open question or stated assumption — never silently invent.

On an **amend** (handed an approved spec + a change request), edit in place — scope the change, re-make the feature's internal chain (AC/state/I-O/edge), analyze the bidirectional ripple (upstream PRD trace, internal, downstream technical-design/test-plan/api-spec), version + changelog, and mark superseded content — never regenerate the whole spec.

## Output

A comprehensive feature spec meeting the **implementability + testability bar** (every feature traced, behavior unambiguous, I/O + states complete, edge cases covered with handling, acceptance criteria testable) — the same bar `reviewing-feature-spec` asserts. Structure from the template; this skill supplies the content quality.

## Key guarantees

- **Composes, not duplicates** — defers structure to the template tool; supplies method + judgment.
- **PRD is upstream input** — elaborates named features; never a blank page.
- **Testable by construction** — edge cases carry handling; acceptance criteria are independently verifiable (metric-threshold for a probabilistic feature).
- **Amends in place** — on a change request, edits the affected blocks + versions + analyzes the bidirectional ripple; never regenerates.
- **Single-sourced bar** — shared with the reviewer, so produce and review don't drift.
- **capability-record-aware** — when a `capability_record` is injected by the caller, scope boundaries are drawn from `owns`/`refs`/`publishes`/`consumes`; graceful fallback when absent.

## License

MIT © 2026 Bhushan Modi.
