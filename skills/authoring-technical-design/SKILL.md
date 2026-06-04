---
name: authoring-technical-design
description: >
  Use when authoring a technical-design document (a TDD / engineering design
  doc / design RFC) for one feature or component — the detailed implementation
  design for building it within an existing system. Guides the producer through
  the METHOD, not the outline: grounding the design in established design-doc
  practice and the project's real constraints, tracing every decision to a
  requirement, comparing at least one real (non-strawman) alternative with a
  stated decision criterion, referencing the architecture-doc / API spec /
  data-model rather than duplicating them, and addressing failure modes,
  testing, and rollout — to a bar where an engineer can implement the feature
  without re-deriving the design. Composes with a separate technical-design
  template tool (section structure) and a deep-research capability. Assumes the
  approved PRD + feature-spec as upstream input — never a blank page. Not for
  system-wide architecture, not for the API contract or data schema, and not
  for reviewing a finished TDD.
extensions:
  claude:
    when_to_use: "designing how to build one feature into an implementable technical design doc"
    argument-hint: "<the feature-spec'd feature (+ PRD / architecture / api-spec / data-model context) to design>"
version: "1.1.0"
forge:
  status: reviewed
  forged: 2026-06-04
  reviewed: 2026-06-04
---

# `authoring-technical-design` — SKILL.md

> **Variant:** standard · **When to use:** designing how to build one feature/component into a technical design doc — to a bar an engineer can implement from without re-deriving the design.

## Overview

This skill is the *how-to* of writing a strong technical design document (TDD) — the detailed implementation design for **one feature or component** within an existing system. The PRD says *what* the product does and the feature-spec says *how each feature behaves*; the TDD says *how this feature will be built* — the chosen approach, the components and their responsibilities, the control + data flow, the key interfaces, the significant logic, the failure modes, the alternatives weighed, the testing, and the rollout. This skill carries the producer's judgment — a **design-research method** and an **implementability bar** — **not** the section list. It assumes two collaborators: a **technical-design template tool** that supplies the section *structure*, and a **deep-research capability** to ground the design in evidence. The producer is handed the **approved PRD + feature-spec** (and, where they exist, the architecture-doc + API spec + data-model) and must **elaborate how to build** the feature — never emit a generic skeleton. The bar to clear: an engineer can implement the feature from the doc without re-deriving the design, and the chosen approach is justified against at least one real alternative.

## When to activate

- Authoring a TDD for one feature-spec'd feature/component, designing how it will be built within the existing system.
- Deciding and documenting the implementation approach: component decomposition, control/data flow, interfaces, detailed logic, failure modes, testing, and rollout.
- Filling a technical-design template with researched, decision-complete content traced to the feature's requirements.

**Do NOT activate when:**

- Designing the whole system's structure, service topology, or long-lived technology choices → that is a higher-altitude **architecture document**. A TDD designs one feature *within* that architecture and references it.
- Authoring the **API contract** (the wire/endpoint surface) or the **data model** (the persisted schema) themselves → those are their own documents this TDD *references*, never duplicates.
- Authoring the PRD or the feature-spec → those are *upstream input* here.
- Reviewing or grading a finished TDD → use a design-review gate.

## Inputs

Read **every document the plan hands you** — your `depends_on` set (the upstream documents discovery determined inform this one) — and trace this document's content back to them. Do not assume a fixed input: the typical upstreams this skill names are method guidance, not a cap on what you receive. Be **self-contained** — produce the document from *whatever* context you actually receive; when an expected informing document is absent, proceed on what you have and surface the gap as an explicit assumption, never fabricate to fill it. And **use a research capability where one is available** (deep-research) to make the document comprehensive and exhaustive, not merely to fill the template.

## Workflow

### Step 1: Take the structure from the template tool — don't invent an outline

Get the section structure from your technical-design template tool (comprehensive variant). Do **not** restate or re-derive a section list here; this skill supplies the method that *fills* those sections well. If no template is available, obtain a comprehensive technical-design structure (request/forge one), then proceed. The genre's load-bearing sections — context/problem, requirement trace, chosen approach + component decomposition, control + data flow, interfaces/contracts, detailed design, error handling, alternatives, testing, rollout/migration — come from the template; your job is the *content quality* that fills them.

### Step 2: Load the upstream docs; drive the design off the requirements

Read the approved PRD + feature-spec — this is your **input, not a blank page** — and, where they exist, the architecture-doc (the system the feature must fit), the API spec, and the data-model. The feature-spec's requirements and acceptance criteria are your coverage checklist: every design decision must trace back to one. Where upstream is thin, make the gap an **explicit open question or stated assumption**, never a silent default. If a feature can't be credibly designed from what's given, surface it as a blocker rather than inventing.

### Step 3: Research to ground the design

Use a deep-research pass to ground the design in two places: (a) **established engineering-design practice** — how the design-doc / RFC genre handles this kind of problem (proven patterns, not invention), and (b) **the project's actual constraints** — the existing architecture, stack, and code the feature plugs into. Design *with* the grain of what exists. **If no research capability is available, do NOT fabricate** approaches, limits, or interfaces — state them as explicitly-flagged assumptions to validate before build.

### Step 4: Apply the design method per section

Fill the template's sections to this method. Collapse a section a thin feature doesn't need (no concurrency → no concurrency prose).

- **Context + requirement trace** — state the feature and the problem at feature scope; **link** deeper material rather than inlining it. List the requirements the design must satisfy and **trace each back** to a PRD goal / feature-spec criterion / constraint. A design decision with no requirement behind it is scope creep; a requirement with no design is a coverage gap. Distinguish goals from **non-goals** — things that could reasonably be goals but are a deliberate exclusion (name them, so reviewers know it was a choice).
- **Chosen approach + component decomposition** — a short overview first, then decompose into components/modules with **one responsibility each** and their collaborators. Position them against the existing system — **reference** the architecture-doc for the surrounding structure, don't redraw it.
- **Control + data flow** — render the primary runtime path as a diagram **and** narrate it step by step; keep the diagram and the prose **in sync**. Success path here; failures go in error handling.
- **Key interfaces + contracts** — give the signatures / message shapes / events the feature introduces or changes, as the *contract* (not the implementation). For anything an **API spec or data-model already owns, reference it and state only the delta** — never re-list endpoints or re-declare a schema (duplication drifts).
- **Detailed design** — only the **non-obvious, load-bearing** logic: the core algorithm(s), the state held and its transitions, and any concurrency / ordering / idempotency concerns. Trivial CRUD needs no prose.
- **Error handling + failure modes** — enumerate each failure (bad input, dependency failure/timeout, partial failure) with its **detection, handling/recovery, and user-visible effect**, plus the retry / timeout / idempotency stance. Not just the happy path.
- **Alternatives considered** — at least **one real, non-strawman alternative** a competent engineer might genuinely have chosen, with its trade-offs and **the decision criterion** that settled the choice. This section exists to force the trade-off thinking — a single rubber-stamped option is a smell.
- **Testing approach** — the unit/integration/end-to-end coverage, the failure cases from above, and conformance testing for any contract the feature exposes; **reference the feature-spec's acceptance criteria** rather than restating them.
- **Rollout, migration + risks** — how it ships, the migration + backward-compatibility stance, flagging/phasing, observability (what to monitor), the rollback plan, and the residual risks + open questions for the reviewer.

### Step 5: Self-check against the implementability bar before handing off

Confirm all hold (this is the bar a runtime design-review gate will assert — author and reviewer share it so they don't drift):

1. **Requirement trace complete** — every functional + non-functional requirement is present and traced to a source; no orphan decisions, no uncovered requirement.
2. **Approach + decomposition implementable** — components and responsibilities are concrete enough to build; the control + data flow is shown as a diagram **and** narrated, and the two agree.
3. **At least one real alternative with a decision criterion** — a genuine (non-strawman) option is compared via trade-offs and the criterion that settled the choice is stated.
4. **Reference, not duplicate** — interfaces and data touchpoints an API spec / data-model / architecture-doc already own are **referenced** with only the delta stated; nothing inlined.
5. **Failure modes addressed** — the significant failures are enumerated with their designed handling/recovery.
6. **Testing addressed** — the verification approach is stated in testable terms, including the failure cases and any contract conformance.
7. **Rollout/migration addressed** — how it ships, migration + backward-compat, observability, and rollback.
8. **Assumptions explicit** — every unknown is surfaced as an assumption/open question, not silently defaulted.
9. **Grounded, not boilerplate** — the design reflects this feature's specifics and the real surrounding system.
10. **Scoped to one feature** — the doc designs one feature/component *within* the architecture; system-wide structure is referenced, not redesigned.

**Thin-input gate:** if a feature can't be designed from what's given or even credibly assumed, surface it as a **blocker** ("design under-specified — needs an architecture/product decision") rather than papering it with an invented approach.

## Rules

**Hard rules (never violate):**

- **Trace every decision to a requirement.** No design choice without a PRD/feature-spec line behind it; no requirement left undesigned.
- **Reference, don't duplicate.** Interfaces, schemas, and system structure owned by an API spec / data-model / architecture-doc are *referenced* with only the delta stated. Inlining them creates drift between the TDD and the source of truth.
- **At least one real alternative.** Compare a genuine alternative with its trade-offs and a stated decision criterion. A strawman or a single un-weighed option does not satisfy the section.
- **Failure modes carry their handling.** Listing a failure without naming its detection and recovery is not done.
- **Never fabricate the design.** Don't invent approaches, limits, or interfaces to look complete. With no source, state them as **explicitly-flagged assumptions** to validate before build.
- **Compose, don't duplicate the outline.** Take the section structure from the template tool; this skill is the method that fills it. Do not paste a competing outline.
- **Design one feature, not the system.** Stay at feature/component altitude; reference the architecture for everything system-wide.
- **Implementable or not done.** Don't hand off a design an engineer must re-derive to build.

**Preferences (override-able):**

- "Comprehensive" sets output *ambition*; stay **proportional** — completeness of the load-bearing *decisions*, not word count. Design docs trend short; a small feature collapses sections it doesn't need.
- Prefer a sequence diagram for message exchanges and a flowchart for decision/data flow; always pair the diagram with a numbered narration.
- Express detailed logic as fenced pseudo-code (the contract / the algorithm shape), not the final implementation.

## Gotchas

- **Designing the system instead of the feature.** Redrawing the service topology or re-deciding the datastore is architecture work, a higher altitude. Reference it; design the one feature within it.
- **Inlining the API or the schema.** Pasting the endpoint list or the table DDL duplicates the API spec / data-model and drifts the moment either changes. Link to the owning doc and state only the delta the feature needs.
- **Strawman alternatives.** "Alternative: do nothing / rewrite everything" isn't a real trade-off. The alternative must be a design a competent engineer might genuinely have chosen, with the criterion that ruled it out.
- **Happy-path-only design.** A flow that never fails isn't designed. Enumerate the failure modes and their recovery — that's where implementation bugs hide.
- **Diagram and prose drift.** A sequence diagram that shows steps the narration omits (or vice versa) leaves the reader guessing. Keep them in sync.
- **Restating the template outline.** Re-deriving the section list inside the content (or in this skill) duplicates the template tool and drifts from it — fill its sections with judgment instead.

**Worked contrast — vague (compliant on the surface) vs implementable** (use it to self-detect):

| Aspect | Vague / un-buildable (reject) | Implementable (ship) |
|---|---|---|
| Requirement trace | "This designs the export feature." | "Designs feature-spec §3.1 *CSV export*; satisfies acceptance criterion 'export completes < 5s for 10k rows'." |
| Decomposition | "An exporter component handles export." | "`ExportJob` (queues + tracks state) delegates row streaming to `RowSerializer`; reads via the existing `ReportQuery` port — see architecture-doc §Reporting." |
| Interfaces | "It calls the report API." | "Reuses `GET /reports/{id}/rows` (api-spec §Reports); this feature adds only a `format=csv` query param — delta noted there." |
| Alternatives | "We picked the best approach." | "Chose streaming over buffering: buffering is simpler but OOMs past ~50k rows; criterion = bounded memory under the 10k-row target." |
| Failure mode | "Errors are handled." | "If `ReportQuery` times out mid-stream, the job is marked `failed`, the partial file is discarded, and the user sees a retryable error." |

If your fill reads like the left column — true of any feature, no trace, no concrete component, no criterion, no handling — it isn't done.

## Anti-patterns

- **"I'll restate the architecture so the doc is self-contained."** That duplicates the architecture-doc and drifts; reference it and design the feature within it.
- **"I'll paste the API/schema so reviewers don't have to look."** Inlining a contract the API spec / data-model owns guarantees drift — link and state only the delta.
- **"One option is obviously right, alternatives are busywork."** The alternatives section forces the trade-off thinking; name a real one and the criterion, or the choice is unjustified.
- **"The happy path is the design; failures are an implementation detail."** Failure modes are where the design earns its keep — enumerate them with handling.
- **"I'll write the outline myself."** Duplicates the template tool — take the structure from it.
- **"Skip the research, I know design docs."** The research grounds *this* system's constraints and the proven patterns for *this* problem — not design-doc theory.

## Output

A **comprehensive technical design document** that meets the **Step 5 implementability bar** (every decision traced to a requirement, an implementable approach + decomposition, control/data flow as a synced diagram + narration, interfaces/data referencing their owning docs, failure modes + testing + rollout addressed, at least one real alternative with a decision criterion, assumptions explicit, scoped to one feature). Expressed **textually** in the markdown medium — prose + a Mermaid sequence/flow diagram + fenced interface/pseudo-code + a trade-off table; the method and bar are medium-independent. The **abstract consumer** is the engineers who implement the feature, and a runtime design-review gate (which asserts the same bar). The TDD **depends on** the PRD + feature-spec (and the architecture-doc / API spec / data-model where present) as input. Its *structure* comes from the template tool; this skill supplies the *content quality*.

## Related

- A **technical-design template tool** (e.g. a content/template gateway) — supplies the section structure this skill fills. Compose with it; never restate its outline.
- A **deep-research capability** — grounds the design in established design-doc practice and the project's actual constraints.
- The **upstream PRD + feature-spec** — the requirements this design elaborates (input, never re-authored here).
- An **architecture-doc / API spec / data-model**, where they exist — the system, contract, and schema the TDD *references* (and may name new ones it requires), never duplicates.
- A **design-review gate** — asserts the same implementability bar on the finished TDD at runtime; author and reviewer share one bar so they don't drift. (Engineering design docs are gated by the generic design-review gate, not a doc-type-specific reviewer.)

## Progressive disclosure

- `references/sources.md` — research provenance for the method + implementability bar (Google "Design Docs at Google", The Pragmatic Engineer RFC/design-doc surveys, Squarespace/Fuchsia RFC templates, single-source-of-truth API-design guidance). Load only to audit where the guidance came from.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap). Claude truncates the combined `description` + `when_to_use` at 1,536 chars in the skill listing.
- Body ≤ ~500 lines / 5,000 tokens.
- Heavy content lives in `references/`, loaded on demand.
