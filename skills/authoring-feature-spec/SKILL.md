---
name: authoring-feature-spec
description: >
  Use when authoring a feature specification (functional spec) — elaborating the
  features a PRD names into implementable, testable detail. Guides the METHOD, not
  the outline: tracing each feature to a PRD goal; specifying observable behavior
  (use-case flows, EARS); enumerating I/O, a state-transition table, and decision
  tables for combinatorial rules; covering edge cases + errors with their handling;
  writing testable Given/When/Then (or metric-threshold, for probabilistic/ML)
  acceptance criteria; applying a per-feature non-functional-requirement taxonomy
  keyed to the feature archetype (UI/API/data-ML/batch/integration/CLI); and
  amending an approved spec as a versioned, ripple-analyzed delta — to a bar an
  engineer can build and a tester can verify each feature from. Composes with a
  feature-spec template tool + a deep-research capability. Assumes the approved PRD
  as upstream input — never a blank page. Not for authoring the PRD, reviewing a
  finished feature spec, or engineering design docs (ADR/RFC).
extensions:
  claude:
    when_to_use: "elaborating a PRD's named features into a testable feature spec (greenfield or a versioned amend)"
    argument-hint: "<the PRD (or features) to elaborate, or the approved spec + change request to amend>"
version: "1.2.0"
forge:
  status: reviewed
  forged: 2026-06-04
  reviewed: 2026-06-14
---

# `authoring-feature-spec` — SKILL.md

> **Variant:** standard · **When to use:** elaborating the features a PRD names into a comprehensive, testable feature specification — to a bar the downstream build can be planned and verified from. Greenfield, or a versioned amend of an approved spec.

## Overview

This skill is the *how-to* of writing a strong feature specification — the layer **below** the PRD. The PRD says *what* the product does and *why*, and **names** its features; the feature spec says *how each named feature behaves*, in enough detail to build and test. This skill carries the producer's judgment — the research method and the quality bar — **not** the section list. It assumes two collaborators: a **feature-spec template tool** that supplies the section *structure*, and a **deep-research capability** to ground each feature in evidence. The producer is handed the **approved PRD (and any upstream context)** and must **decompose and elaborate** its features — never emit generic boilerplate. The bar to clear: each feature is *implementable and testable* — an engineer can build it and a tester can verify it without asking the author, and planning can cut tasks from it.

The method spine is unchanged from a strong feature spec; this version **deepens** how you write unambiguous behavior (EARS, use-case flows, the requirements-smell catalog), makes the state-transition table and decision table explicit, adds a per-feature **non-functional-requirement** discipline and **archetype overlays** (a feature's emphasis shifts by its nature), handles **probabilistic/ML** features (threshold criteria, not "works"), and adds an **amend** method for the common case of changing an approved spec.

## When to activate

- Authoring a feature spec from an approved PRD that names a set of features.
- Elaborating one feature (or a clearly-bounded set) into testable behavior, I/O, states, edge cases, and acceptance criteria.
- **Amending** an approved feature spec (a delta: a feature/behavior/AC/state changed or added) — you are handed the existing spec + a change request.
- Filling a feature-spec template with researched, decision-complete per-feature content.

**Do NOT activate when:**

- Authoring the PRD itself (problem, users, metrics, MVP boundary) → use a PRD-authoring skill. The PRD is *upstream input* here.
- Reviewing or grading a finished feature spec → use a feature-spec-review skill.
- Writing an engineering design doc (ADR, RFC, architecture) — that is the *how it's coded* layer **downstream** of this one.

## Inputs

Read **every document the plan hands you** — your `depends_on` set (the upstream documents discovery determined inform this one) — and trace this document's content back to them. The typical upstream is the **approved PRD**; a **UI** feature may also receive user-flows / wireframes / a design-system; a **data/ML** feature may receive a data spec. These are method guidance, not a fixed cap. Be **self-contained** — produce from *whatever* context you actually receive; when an expected informing document is absent, proceed on what you have and surface the gap as an explicit assumption, never fabricate to fill it. And **use a research capability where one is available** (deep-research) to make the document comprehensive, not merely to fill the template. On an **amend**, you are additionally handed the existing spec + the change request (and, where the ripple must be checked, the relevant downstream docs).

## Workflow

### Step 1: Take the structure from the template tool — don't invent an outline

Get the section structure from your feature-spec template tool (comprehensive variant). Do **not** restate or re-derive a section list here; this skill supplies the method that *fills* those sections well. The comprehensive template repeats a per-feature block and carries the version header, behavior (+ a decision table), I/O + data contract, the state-transition table, edge cases, error handling, acceptance criteria, a non-functional-requirements section, dependencies, open questions, and a versioning/changelog section. If no template is available, obtain a comprehensive feature-spec structure (request/forge one, or fall back to the canonical per-feature set), then proceed. **Proportionality:** the template is comprehensive; your *fill* is proportional — a thin feature legitimately leaves the state table, decision table, NFR, or changelog empty.

### Step 2: Load the PRD; drive coverage off its feature list; identify each feature's archetype

Read the approved PRD and any upstream documents it depends on — this is your **input, not a blank page**. List every feature the PRD names; that list is your coverage checklist. **Decompose** the PRD into per-feature specs: each feature gets its own block. For each feature, name its **archetype** (UI · REST/API · data-ML · batch/async-job · integration/webhook · CLI — a feature may be several at once); the archetype shifts which sections carry weight (Step 4). Before drafting a feature, fill knowledge gaps about *its* behavior — and where the PRD is thin, make the gap an **explicit open question or stated assumption**, never silently generic. If a PRD feature can't even be credibly elaborated, surface it as a blocker rather than inventing behavior.

### Step 3: Research to ground each feature

Use a deep-research pass to ground each feature's behavior, domain rules, and edge cases in evidence — the specific domain of *this* product, not "feature specs in general." **If no research capability is available, do NOT fabricate behavior, limits, or error codes** — state them as explicitly-flagged assumptions to validate before build.

### Step 4: Apply the per-feature method

Fill the template's per-feature sections to this method. Repeat per feature; collapse a section a thin feature doesn't need (no state → no state table). Depth for each angle is in `references/` — load it when a section needs the full treatment.

- **Purpose & PRD trace** — state the one job this feature does and **link it back to a specific PRD requirement / goal / metric** (forward+backward traceability). A feature with no PRD line behind it is scope creep; a PRD line with no feature is a coverage gap. Quote/reference the exact PRD item.
- **Behavior & interactions** — describe how the system responds **observably** and **implementation-free** (the *what*, not the *how*). Write the **main success scenario** as ~3–11 steps (each "actor does X → system responds Y"); then **alternate flows** (a different path where the goal is *still met*) and **exception flows** (a path where the goal is *not met*, each naming its handling). Prefer **EARS** phrasing per behavior statement ("When `<trigger>`, the system shall `<response>`"; "While `<state>`…"; "If `<unwanted condition>`, then…") — it makes the behavior atomic and maps 1:1 to an acceptance criterion. Derive the edge-case set by walking each step and asking "what can fail/vary here?". See `references/requirement-and-behavior.md`.
- **Decision table (combinatorial rules)** — when the response depends on a *combination* of conditions, specify it as a conditions × rules → actions table so every combination has a defined action and missing/contradictory rules surface. (Aid; skip when behavior isn't combinatorial.)
- **Inputs / outputs & data** — enumerate every input (source, type, validation rule, required/optional) and every output (response shape, side effects, error codes) as a **contract** a caller validates against; for each input ask "what's valid, what's not, what's the boundary"; for each output, "what does the caller/UI observe." Note entities read/written and persisted vs transient.
- **States & transitions** — if stateful, specify a **state-transition table**: current state × event → next state, with a dash for an **illegal** transition; name initial and terminal states. The table form is what makes illegal transitions checkable.
- **Edge cases & error handling** — enumerate boundary/failure paths (boundary-value: just below/at/just above each limit; null/empty, duplicate/idempotency, concurrency/race, permissions/visibility, limits/overflow). **Every edge case and error names its expected handling** — the response/message/recovery — not just its existence. (Edge = valid-but-unusual; error = failure — name both.)
- **Acceptance criteria** — each behavior and key edge/error case carries criteria a tester can run **pass/fail**: **Given/When/Then** (scenario form) or a rule-based checklist. **1–3 per feature**; 4+ usually means two features hide inside one — **split**. For a **probabilistic/ML** feature a deterministic G/W/T mis-fits the output — write **metric-threshold criteria on a named dataset** ("precision ≥ 0.85 on the `<eval-set>`"), plus the **low-confidence/fallback** behavior and the **data requirements** (sources/ranges/balance). "The model is accurate" is not a criterion. See `references/io-states-archetype-amend.md`.
- **Non-functional requirements** — list the **applicable** NFR categories for this feature, each with a **numeric/checkable target** (performance p95; reliability/idempotency; security/authorization; privacy; accessibility WCAG 2.2 AA for UI; limits/quotas; compatibility). Proportional — a trivial feature needs none; "should be fast/secure" is not an NFR.
- **Archetype emphasis** — apply the overlay for the feature's nature (UI → per-state behavior + a11y + microcopy; API → request/response schema + status/error model + idempotency + rate-limits [hand the wire contract to api-spec]; data-ML → data requirements + threshold AC + drift/fallback; batch → schedule + idempotency + partial-failure/retry; integration → delivery semantics + payload contract; CLI → args/flags + exit codes). The overlay is a *what-to-cover* aid, kept proportional. See `references/io-states-archetype-amend.md`.
- **Cross-cutting (applies across features, not a section)** — one idea per statement (singular), consistent terminology, no contradictions; scan each requirement/AC against the **requirements-smell catalog** (subjective language, ambiguous adverbs, non-verifiable/weak terms, comparatives without a referent, loopholes, open-ended "etc.") and rewrite any load-bearing hit to a quantifiable/observable statement.

### Step 5: Amend an approved spec (when handed a change request)

When the input is an existing approved spec + a change request, **do not regenerate the whole spec** — amend it in place:

1. **Scope the change** — state which features/behaviors/AC/states/I-O-fields this delta touches and what is deliberately untouched.
2. **Edit in place** — change only the affected blocks.
3. **Re-make the feature's internal chain consistent** — after changing a behavior, update its AC, state table, I/O, and edge cases so the feature stays self-consistent.
4. **Analyze the bidirectional ripple** — **upstream** (does it still trace to a PRD line? if it adds an un-traced feature, flag "the PRD must be amended first"), **internal** (which AC/state/I-O/edge are now stale — fixed in step 3), **downstream** (which technical-design decisions / test cases / api-spec entries are now stale — list them as the affected set).
5. **Version + changelog** — bump the document's own version header; add a changelog entry (who/when/what/why).
6. **Mark superseded content** — mark outdated behaviors/criteria/states superseded with the reason; don't silently delete. See `references/io-states-archetype-amend.md`.

### Step 6: Self-check against the implementability bar before handing off

Confirm all hold (this is the bar a reviewer will assert — author and reviewer share it so they don't drift):

1. **Traced to the PRD** — every feature maps back to a specific PRD requirement/metric; no orphan features, no uncovered PRD lines.
2. **Unambiguous behavior** — each behavior is interpretable exactly one way, implementation-free, observable; flows classified (main/alternate/exception); no load-bearing requirements-smell.
3. **Complete I/O + states** — inputs (with validation) and outputs (with shape/side-effects) enumerated; stateful features carry a state-transition table (legal cells + illegal markers); combinatorial rules carry a complete decision table.
4. **Edge cases covered *with handling*** — null/empty, duplicate/idempotency, concurrency, permissions, limits each named **with their expected error/handling**.
5. **Testable acceptance criteria** — each behavior/edge case has independently-testable pass/fail criteria (G/W/T or rule-based; metric-threshold for a probabilistic feature).
6. **Singular + consistent** — one idea per requirement, terminology consistent, no internal contradictions.
7. **Feasible + plannable** — buildable within stated constraints; I/O + criteria concrete enough to cut tasks/milestones from.
8. **Open questions surfaced** — genuine unknowns + unresolved decisions are stated openly (not papered as settled fact); design assumptions are flagged, never silent guesses.
9. **Non-functional targets present where warranted** — the feature's load-bearing NFR categories carry numeric targets (proportional).
10. **(Amend only) delta is scoped, ripple-clean, versioned** — change is in-scope, still PRD-traced (or an upstream PRD amend is flagged), the internal chain is consistent, downstream ripple is surfaced, the version + changelog are updated, superseded content is marked.

**Thin-input gate:** if a PRD feature's behavior cannot be researched or even credibly assumed, surface it as a **blocker** ("feature under-defined — needs product decision") rather than papering it with invented behavior.

## Rules

**Hard rules (never violate):**

- **Trace every feature to the PRD.** No orphan feature and no uncovered PRD feature. Coverage runs off the PRD's feature list.
- **Behavior is observable and implementation-free.** Specify *what* the feature does, not *how* it's coded — that is the downstream design layer.
- **Edge cases and errors carry their handling.** Listing a case without naming its expected response is not done.
- **Acceptance criteria are testable.** G/W/T or rule-based (or metric-threshold for a probabilistic feature). A criterion you can't make pass/fail means the behavior isn't specified yet.
- **No vague language.** Replace subjective words ("fast", "robust", "user-friendly") and the smell-catalog terms with **quantifiable/observable** statements ("p95 < 200 ms", "returns 409 on duplicate key"). "The model is accurate" is not a criterion.
- **Never fabricate behavior.** Don't invent limits, error codes, or rules to look complete. With no source, state them as **explicitly-flagged assumptions** to validate before build.
- **Compose, don't duplicate.** Take the section structure from the template tool; this skill is the method that fills it.
- **Elaborate the PRD, don't re-author it.** Don't restate its problem/users/metrics or re-decide *which* features exist.
- **Amend in place, don't regenerate.** On a change request, edit the affected blocks, version + changelog, mark superseded, and analyze the bidirectional ripple — never silently re-emit the whole spec.
- **Implementable + testable or not done.**

**Preferences (override-able):**

- "Comprehensive" sets output *ambition*; stay **proportional** — completeness of *decisions*, not word count. A thin feature collapses sections it doesn't need (no NFR, no state table, no decision table, no changelog on a first draft).
- Prefer EARS for behavior statements and Given/When/Then for scenarios; use a rule-based checklist for invariants/validation tables; use metric-thresholds for probabilistic outputs.
- Keep acceptance criteria to **1–3 per feature**; 4+ is a split smell (INVEST "Small"/"Testable").

## Gotchas

- **Spec that re-authors the PRD.** Restating problem/users/metrics, or re-deciding the feature set — that's PRD work. Decompose and detail; don't re-litigate scope.
- **Behavior that leaks implementation.** "Stores the token in Redis with a 1h TTL" is *how it's coded* — downstream. Specify the observable contract ("the session is valid for 1h, then re-auth is required").
- **Edge cases listed but unhandled.** "Edge case: concurrent edits" with no resolution is a question, not a spec.
- **Untestable acceptance criteria.** "The feature works correctly" / "errors are handled gracefully" / "the model is accurate" can't be run pass/fail.
- **Deterministic criteria on a probabilistic feature.** A model/ranker needs metric-threshold criteria on a named dataset + a fallback, not Given/When/Then over a fixed output.
- **State listed without the table.** Listing states but leaving transitions (especially the illegal ones) to be guessed is under-specified — use the states×events table with dashes for illegal cells.
- **Criteria sprawl = hidden second feature.** 4+ acceptance criteria usually bundles two behaviors. Split it.
- **Archetype/NFR as a section-presence checkbox.** The overlays + NFR are *proportional aids* — a thin feature legitimately omits them; don't pad to look complete.
- **Amend by regeneration.** Re-emitting the whole spec on a small change loses provenance and risks silent drift — amend in place + changelog + ripple.

**Worked contrast — vague (compliant on the surface) vs implementable** (use it to self-detect):

| Aspect | Vague / un-buildable (reject) | Implementable (ship) |
|---|---|---|
| PRD trace | "This feature is about invoices." | "Implements PRD §4.2 *Auto-reminders*; advances metric 'cut median days-to-payment 21→14'." |
| Behavior | "The system sends a reminder." | "When an invoice is 3 days past due *and* unpaid, the system emails the client the reminder template; logs a `reminder_sent` event." |
| Edge case | "Handle the case where the invoice is paid." | "If the invoice is paid before the 3-day mark, **no** reminder is sent; a reminder already queued is cancelled." |
| Error handling | "Email errors are handled." | "If the email provider returns 5xx, retry 3× with backoff; after that, mark `reminder_failed` and surface it in the dashboard." |
| Acceptance (deterministic) | "Reminders work." | "Given an unpaid invoice 3 days overdue, when the daily job runs, then exactly one reminder email is sent and a `reminder_sent` event is recorded." |
| Acceptance (probabilistic) | "The relevance model is accurate." | "On the `2026-Q2-holdout` set, precision@10 ≥ 0.80 and recall@10 ≥ 0.65; on confidence < 0.4 the result falls back to recency sort." |

If your fill reads like the left column — true of any feature, no trigger, no observable outcome, no handling — it isn't done.

## Anti-patterns

- **"I'll re-state the PRD's features in my own words."** That's not elaboration — add behavior, I/O, states, edge cases, and criteria the PRD doesn't carry.
- **"I'll describe how it's implemented to be precise."** Implementation belongs to the downstream design layer.
- **"I'll list the edge cases; handling is obvious."** Name the expected handling for each, or it's an open question.
- **"'Works as expected' / 'the model is accurate' is a fine acceptance criterion."** Untestable — forbidden. Make it observable (or a metric threshold on a dataset).
- **"One big feature block keeps it together."** 4+ criteria/sprawling behavior means split.
- **"I'll add a UI/API/ML/NFR section to look thorough."** Archetype + NFR are proportional — only where the feature warrants them.
- **"I'll just regenerate the spec for this change."** Amend in place; version + changelog + ripple.
- **"I'll write the outline myself."** Duplicates the template tool.

## Output

A **comprehensive feature specification** (or a scoped, versioned **amend** of one) that meets the **Step 6 implementability bar** (every feature traced to the PRD, unambiguous observable behavior with classified flows, complete I/O + a state-transition table, combinatorial rules in a decision table, edge cases covered *with handling*, testable acceptance criteria [G/W/T or metric-threshold], applicable NFR targets, singular + consistent, feasible + plannable, open questions surfaced; an amend additionally scoped + ripple-clean + versioned). The **abstract consumer** is the downstream planning phase, the engineers who build it, the testers who verify it, and a reviewer (which asserts the same bar). The feature spec **depends on the PRD** as input; its *structure* comes from the template tool; this skill supplies the *content quality*. **Medium:** the artifact is a **textual-markdown document** today; the method is medium-independent (it applies equally if the spec lives in another store).

## Related

- A **feature-spec template tool** (e.g. a content/template gateway) — supplies the per-feature section structure this skill fills. Compose with it; never restate its outline.
- A **deep-research capability** — grounds each feature's behavior, domain rules, and edge cases in evidence.
- A **PRD-authoring skill** — produces the *upstream* PRD this skill's input depends on. On an amend that adds an un-traced feature, the PRD is amended first.
- A **feature-spec-review skill** — asserts the same implementability/testability bar (incl. the delta-scoped amend review) on the finished spec; author and reviewer share one bar so they don't drift.
- The **downstream consumers** — technical-design (the how), test-plan (the verification), api-spec (the wire contract) — this spec feeds them; the amend ripple analysis names which are affected by a change.

## Progressive disclosure

- `references/requirement-and-behavior.md` — the ISO/IEC/IEEE 29148 quality attributes, the EARS pattern set, the requirements-smell catalog, and the use-case main/alternate/exception flow method. Load when writing or sharpening behavior + acceptance.
- `references/io-states-archetype-amend.md` — the I/O data contract, the state-transition-table + decision-table forms, the feature-level NFR taxonomy with numeric bars, the six archetype overlays (incl. probabilistic/ML), and the amend ripple procedure. Load when a feature is stateful, combinatorial, archetype-specific, or being amended.
- `references/sources.md` — research provenance for the method + quality bar. Load only to audit where the guidance came from.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap).
- Body ≤ ~500 lines / 5,000 tokens.
- Heavy content lives in `references/`, loaded on demand.
