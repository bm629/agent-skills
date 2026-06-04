---
name: authoring-feature-spec
description: >
  Use when authoring a feature specification (functional spec) — elaborating the
  features a PRD names into implementable, testable detail. Guides the producer
  through the METHOD, not the outline: tracing each feature back to a PRD goal,
  specifying observable behavior and interactions, enumerating inputs/outputs +
  states, covering edge cases and error handling with their expected handling,
  and writing testable Given/When/Then acceptance criteria — to a bar where an
  engineer can build each feature and a tester can verify it without asking the
  author. Composes with a separate feature-spec template tool (which supplies the
  section structure) and a deep-research capability (to ground each feature in the
  PRD and domain). Assumes the approved PRD as upstream input — never a blank page.
  Not for authoring the PRD itself, not for reviewing a finished feature spec, and
  not for engineering design docs (ADR/RFC).
extensions:
  claude:
    when_to_use: "elaborating a PRD's named features into a testable feature spec"
    argument-hint: "<the PRD (or features) to elaborate into a feature spec>"
version: "1.1.0"
forge:
  status: reviewed
  forged: 2026-06-04
  reviewed: 2026-06-04
---

# `authoring-feature-spec` — SKILL.md

> **Variant:** standard · **When to use:** elaborating the features a PRD names into a comprehensive, testable feature specification — to a bar the downstream build can be planned and verified from.

## Overview

This skill is the *how-to* of writing a strong feature specification — the layer **below** the PRD. The PRD says *what* the product does and *why*, and **names** its features; the feature spec says *how each named feature behaves*, in enough detail to build and test. This skill carries the producer's judgment — the research method and the quality bar — **not** the section list. It assumes two collaborators: a **feature-spec template tool** that supplies the section *structure*, and a **deep-research capability** to ground each feature in evidence. The producer is handed the **approved PRD (and any upstream context)** and must **decompose and elaborate** its features — never emit generic boilerplate. The bar to clear: each feature is *implementable and testable* — an engineer can build it and a tester can verify it without asking the author, and planning can cut tasks from it.

## When to activate

- Authoring a feature spec from an approved PRD that names a set of features.
- Elaborating one feature (or a clearly-bounded set) into testable behavior, I/O, states, edge cases, and acceptance criteria.
- Filling a feature-spec template with researched, decision-complete per-feature content.

**Do NOT activate when:**

- Authoring the PRD itself (problem, users, metrics, MVP boundary) → use a PRD-authoring skill. The PRD is *upstream input* here.
- Reviewing or grading a finished feature spec → use a feature-spec-review skill.
- Writing an engineering design doc (ADR, RFC, architecture) — that is the *how it's coded* layer **downstream** of this one.

## Inputs

Read **every document the plan hands you** — your `depends_on` set (the upstream documents discovery determined inform this one) — and trace this document's content back to them. Do not assume a fixed input: the typical upstreams this skill names are method guidance, not a cap on what you receive. Be **self-contained** — produce the document from *whatever* context you actually receive; when an expected informing document is absent, proceed on what you have and surface the gap as an explicit assumption, never fabricate to fill it. And **use a research capability where one is available** (deep-research) to make the document comprehensive and exhaustive, not merely to fill the template.

## Workflow

### Step 1: Take the structure from the template tool — don't invent an outline

Get the section structure from your feature-spec template tool (comprehensive variant). Do **not** restate or re-derive a section list here; this skill supplies the method that *fills* those sections well. The template typically repeats a per-feature block; if no template is available, obtain a comprehensive feature-spec structure (request/forge one, or fall back to the canonical per-feature set: purpose+trace, behavior, I/O+data, states, edge cases, error handling, acceptance criteria, dependencies, open questions), then proceed.

### Step 2: Load the PRD; drive coverage off its feature list

Read the approved PRD and any upstream documents it depends on — this is your **input, not a blank page**. List every feature the PRD names; that list is your coverage checklist. **Decompose** the PRD into per-feature specs: each feature gets its own block. Before drafting a feature, fill knowledge gaps about *its* behavior — and where the PRD is thin, make the gap an **explicit open question or stated assumption**, never silently generic. If a PRD feature can't even be credibly elaborated, surface it as a blocker rather than inventing behavior.

### Step 3: Research to ground each feature

Use a deep-research pass to ground each feature's behavior, domain rules, and edge cases in evidence — the specific domain of *this* product, not "feature specs in general." **If no research capability is available, do NOT fabricate behavior, limits, or error codes** — state them as explicitly-flagged assumptions to validate before build.

### Step 4: Apply the per-feature method

Fill the template's per-feature sections to this method. Repeat per feature; collapse a section a thin feature doesn't need (no state → no state section).

- **Purpose & PRD trace** — state the one job this feature does and **link it back to a specific PRD requirement / goal / metric** (forward+backward traceability). A feature with no PRD line behind it is scope creep; a PRD line with no feature is a coverage gap. Quote/reference the exact PRD item.
- **Behavior & interactions** — describe how the system responds to each input and interaction **observably** and **implementation-free** (the *what*, not the *how*). Walk the primary flow step by step — for each step name the trigger and the system response — then the alternate flows.
- **Inputs / outputs & data** — enumerate every input (source, type, validation rules, required/optional) and every output (response shape, UI/DB change, side effects, error codes). For each input ask "what's valid, what's not, what's the boundary"; for each output, "what does the caller/UI observe." Note the data entities read/written and whether persisted or transient.
- **States & transitions** — if the feature is stateful, list the states and the legal transitions *and the illegal ones*: for each (state × event), name the resulting state or the rejection. Call out initial and terminal states.
- **Edge cases & error handling** — explicitly enumerate boundary and failure paths against a checklist: null/empty, duplicates/idempotency, concurrency/race, permissions/visibility, limits/overflow. **Every edge case and error names its expected handling** — the response/message/recovery — not just its existence. (Edge cases are valid-but-unusual; errors are failures — name both.)
- **Testable acceptance criteria** — each behavior and key edge/error case carries criteria a tester can run **pass/fail**, preferably **Given/When/Then** (scenario form) or a rule-based checklist where G/W/T doesn't fit. Write them **before** implementation — the spec is the contract the test asserts. One criterion per distinct aspect, **1–3 per feature**; needing 4+ usually means two features hide inside one — **split**.
- **Cross-cutting (applies across all features, not a section)** — one idea per statement (singular), consistent terminology, no contradictions across features; non-functional targets (performance, security, reliability) where the feature warrants them, stated as numbers.

### Step 5: Self-check against the implementability bar before handing off

Confirm all hold (this is the bar a reviewer will assert — author and reviewer share it so they don't drift):

1. **Traced to the PRD** — every feature maps back to a specific PRD requirement/metric; no orphan features, no uncovered PRD lines.
2. **Unambiguous behavior** — each behavior is interpretable exactly one way, implementation-free, observable.
3. **Complete I/O + states** — inputs (with validation) and outputs (with shape/side-effects) enumerated; stateful features list states + legal transitions.
4. **Edge cases covered *with handling*** — null/empty, duplicate/idempotency, concurrency, permissions, limits each named **with their expected error/handling**, not merely listed.
5. **Testable acceptance criteria** — each behavior/edge case has independently-testable pass/fail criteria (G/W/T or rule-based).
6. **Singular + consistent** — one idea per requirement, terminology consistent, no internal contradictions.
7. **Feasible + plannable** — buildable within stated constraints; I/O + criteria concrete enough that planning can cut tasks/milestones from them.

**Thin-input gate:** if a PRD feature's behavior cannot be researched or even credibly assumed, surface it as a **blocker** ("feature under-defined — needs product decision") rather than papering it with invented behavior. A feature spec whose behavior, I/O, *and* criteria are all guesses is not implementable.

## Rules

**Hard rules (never violate):**

- **Trace every feature to the PRD.** No orphan feature (no PRD line behind it) and no uncovered PRD feature. Coverage runs off the PRD's feature list.
- **Behavior is observable and implementation-free.** Specify *what* the feature does, not *how* it's coded — that is the downstream design layer.
- **Edge cases carry their handling.** Listing an edge case without naming its expected response/error is not done — name the handling.
- **Acceptance criteria are testable.** Every behavior/edge case has pass/fail criteria (G/W/T or rule-based). A criterion you can't make pass/fail means the behavior isn't specified yet.
- **No vague language.** Replace subjective words ("fast", "robust", "handles errors") with **quantifiable/observable** statements ("p95 < 200ms", "returns 409 on duplicate key"). Vague adjectives are not specifications.
- **Never fabricate behavior.** Don't invent limits, error codes, or rules to look complete. With no source, state them as **explicitly-flagged assumptions** to validate before build. An honest assumption beats an invented constant.
- **Compose, don't duplicate.** Take the section structure from the template tool; this skill is the method that fills it. Do not paste a competing outline.
- **Elaborate the PRD, don't re-author it.** The PRD is upstream input. Don't restate its problem/users/metrics or re-decide *which* features exist — elaborate the features it already named into testable detail.
- **Implementable + testable or not done.** Don't hand off a feature an engineer can't build and a tester can't verify without asking you.

**Preferences (override-able):**

- "Comprehensive" sets output *ambition*; stay **proportional** — completeness of *decisions*, not word count. A thin feature collapses sections it doesn't need.
- Keep acceptance criteria to **1–3 per feature**; 4+ is a smell that the feature should split (INVEST "Small"/"Testable").
- Prefer Given/When/Then for scenarios; use a rule-based checklist for invariants and validation tables where G/W/T reads awkwardly.

## Gotchas

- **Spec that re-authors the PRD.** Restating the problem/users/metrics, or re-deciding the feature set, instead of elaborating the named features — that's PRD work, already done upstream. Decompose and detail; don't re-litigate scope.
- **Behavior that leaks implementation.** "Stores the token in Redis with a 1h TTL" is *how it's coded* — downstream. Specify the observable contract ("the session is valid for 1h, then re-auth is required") and leave the mechanism to design.
- **Edge cases listed but unhandled.** "Edge case: concurrent edits" with no resolution is a question, not a spec. Every edge case names what *should* happen.
- **Untestable acceptance criteria.** "The feature works correctly" / "errors are handled gracefully" can't be run pass/fail. Name the precondition, the action, and the **observable** outcome.
- **Criteria sprawl = hidden second feature.** A feature needing 5+ acceptance criteria usually bundles two behaviors. Split it (INVEST "Small") rather than growing one block.
- **Restating the template outline.** Re-deriving the section list inside the content (or in this skill) duplicates the template tool and drifts from it — fill its sections with judgment instead.

**Worked contrast — vague (compliant on the surface) vs implementable** (use it to self-detect):

| Aspect | Vague / un-buildable (reject) | Implementable (ship) |
|---|---|---|
| PRD trace | "This feature is about invoices." | "Implements PRD §4.2 *Auto-reminders*; advances metric 'cut median days-to-payment 21→14'." |
| Behavior | "The system sends a reminder." | "When an invoice is 3 days past due *and* unpaid, the system emails the client the reminder template; logs a `reminder_sent` event." |
| Edge case | "Handle the case where the invoice is paid." | "If the invoice is paid before the 3-day mark, **no** reminder is sent; a reminder already queued is cancelled." |
| Error handling | "Email errors are handled." | "If the email provider returns 5xx, retry 3× with backoff; after that, mark `reminder_failed` and surface it in the dashboard." |
| Acceptance criterion | "Reminders work." | "Given an unpaid invoice 3 days overdue, when the daily job runs, then exactly one reminder email is sent and a `reminder_sent` event is recorded." |

If your fill reads like the left column — true of any feature, no trigger, no observable outcome, no handling — it isn't done.

## Anti-patterns

- **"I'll re-state the PRD's features in my own words."** That's not elaboration — add behavior, I/O, states, edge cases, and criteria the PRD doesn't carry, or you've added nothing.
- **"I'll describe how it's implemented to be precise."** Implementation belongs to the downstream design layer; the spec states the observable contract.
- **"I'll list the edge cases; handling is obvious."** Obvious to whom? Name the expected handling for each, or it's an open question.
- **"'Works as expected' is a fine acceptance criterion."** Untestable — forbidden. Make it Given/When/Then with an observable Then.
- **"One big feature block keeps it together."** 4+ criteria/sprawling behavior means split — one focused feature per block (INVEST).
- **"I'll write the outline myself."** Duplicates the template tool — take the structure from it.
- **"Skip the research, I know feature specs."** The research grounds *this product's* domain rules and edge cases — not feature-spec theory.

## Output

A **comprehensive feature specification** that meets the **Step 5 implementability bar** (every feature traced to the PRD, unambiguous observable behavior, complete I/O + states, edge cases covered *with handling*, testable acceptance criteria, singular + consistent, feasible + plannable). The **abstract consumer** is the downstream planning phase (which derives build tasks/milestones from each feature), the engineers who build it, the testers who verify it, and a reviewer (which asserts the same bar). The feature spec **depends on the PRD** as input. Its *structure* comes from the template tool; this skill supplies the *content quality*.

## Related

- A **feature-spec template tool** (e.g. a content/template gateway) — supplies the per-feature section structure this skill fills. Compose with it; never restate its outline.
- A **deep-research capability** — grounds each feature's behavior, domain rules, and edge cases in evidence.
- A **PRD-authoring skill** — produces the *upstream* PRD this skill's input depends on (problem, users, metrics, MVP, the feature *list*).
- A **feature-spec-review skill** — asserts the same implementability/testability bar on the finished spec; author and reviewer share one bar so they don't drift.

## Progressive disclosure

- `references/sources.md` — research provenance for the method + quality bar (29148, EARS, BDD/Gherkin, INVEST, RTM). Load only to audit where the guidance came from.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap).
- Body ≤ ~500 lines / 5,000 tokens.
- Heavy content lives in `references/`, loaded on demand.
