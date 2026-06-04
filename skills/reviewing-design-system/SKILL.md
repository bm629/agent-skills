---
name: reviewing-design-system
description: >
  Use when reviewing or judging a finished design-system document — a product's
  reusable visual + interaction language (principles, tokens, a component catalog,
  patterns, accessibility, voice) — deciding whether an engineer can build a
  consistent, accessible UI from it. A gate, not authoring. Judges it against a
  single-sourced usability/consistency/accessibility bar:
  tokens defined and referenced by intent (components use semantic tokens, not
  raw values); components fully specced; the catalog covers the screens'
  components plus an archetype-sized standard set; accessibility numeric (WCAG
  contrast/focus/keyboard); nothing fabricated. Judges a textual markdown artifact,
  not rendered swatches. Emits exactly `VERDICT: approve|revise` plus actionable
  findings; approves a system meeting the bar (no false-revise of a
  proportionally-sized one), revises only on a named gap. Not for authoring it, not
  for per-screen layout (wireframe-review), not for navigation paths
  (user-flow-review), not for engineering design docs.
extensions:
  claude:
    when_to_use: "judging a finished design-system document against the usability + consistency + accessibility bar and emitting an approve/revise verdict"
    argument-hint: "<the finished design-system document to review>"
version: "1.1.0"
forge:
  status: reviewed
  forged: 2026-06-04
  reviewed: 2026-06-04
---

# `reviewing-design-system` — SKILL.md

> **Variant:** standard · **When to use:** judging a finished design-system document as an acceptance gate — checking a designer/engineer can build a consistent, accessible UI from it, then emitting `VERDICT: approve|revise` with actionable findings.

## Overview

This skill is the *review* half of a producing/judging design-system pair. Loaded by a reviewer who holds a **finished design-system document** — the reusable visual + interaction language a product's UI draws on (principles, design tokens, a component catalog, patterns, accessibility standards, and voice) — it judges that document against one question: **can a designer build a consistent UI and an engineer implement it from this document, without asking the author, and does the catalog cover the components the product's screens actually need?** It applies a fixed **usability + consistency + accessibility checklist** — the same bar a design-system author produces to, so the produce-bar and the review-bar do not drift — then emits a single machine-parseable verdict plus findings the author can act on in one revision pass. It judges the **textual markdown artifact** (tokens as values, type-scale and component spec tables), not a rendered design file. It is an acceptance gate — it does **not** author, fix, or rewrite the document; it judges and returns findings, and the producer revises.

## When to activate

- A finished design-system document needs an accept/revise decision before wireframing or UI engineering builds from it.
- You are the independent reviewer / gate for a design system a producer just authored.
- Re-judging a revised design system after a prior `revise` verdict.

**Do NOT activate when:**

- Authoring or repairing a design system -> use a design-system-authoring skill (it produces to the same bar this skill asserts). This skill never writes the document.
- Reviewing a **wireframes / per-screen layout** document — where components are *placed* on a given screen -> use a wireframe-review skill. That gate judges screen structure; **this** gate judges the reusable visual language (tokens + component catalog) one layer up.
- Reviewing a **user-flows** document — the *navigation paths* a user takes through the product -> use a user-flow-review skill. That gate judges flow coverage and dead-ends, not the visual vocabulary.
- Reviewing an **engineering design document** — an architecture spec, design doc, ADR, or RFC -> use a design-review skill that verifies design claims against the codebase. Distinct gate, distinct bar.
- Checking template/section conformance -> that is a template concern. This skill judges *quality against the bar*, not whether every heading is present.
- Grading a **coded** component library (CSS/React) -> this gate judges the *document* (tokens + specs + rules), not an implementation.

## Workflow

### Step 1: Read the whole document with fresh, independent eyes

Read the design system end to end as if encountering it for the first time, without the author's framing. Your stance is a gatekeeper for the *next* steps (wireframing + UI engineering): a finding carries weight only when it shows a designer or engineer **cannot build a consistent, accessible UI as written**. Identify the **product archetype** the system is sized to (a thin CLI/utility vs. a content app vs. a full interactive UI product) and, where available, the product's flows/screen list — Step 2's coverage condition checks the catalog against the surface area the product actually needs. Note where a token, a component spec, or an accessibility target is load-bearing; those are the spots the checklist scrutinizes.

### Step 2: Run the usability + consistency + accessibility checklist — judge each condition

For each condition below, decide **pass** or **gap**. A condition fails only on a *real, named* deficiency — "I'd have chosen a different palette" is not a gap. For each gap, capture the exact location and what is missing (Step 4 turns it into an actionable finding). The conditions are the single-sourced bar; do not add private ones.

1. **Principles stated.** 3–6 **actionable** design principles are present — opinionated beliefs a reviewer could settle a disagreement with, each naming the tradeoff it picks. *Gap* when principles are absent, or are platitudes ("be delightful", "look modern") that decide nothing.
2. **Tokens defined + applied consistently.** Color (including **semantic role** tokens, not just raw ramps), a typography scale, spacing, elevation, and motion are **all** defined as named tokens with concrete values; components reference **semantic** tokens, never raw values. The semantic layer referenced by components is the **consistency guarantee**. *Gap* when a token family is missing or valueless, or when component specs reference raw values (`color.blue.500`, a literal `#1A73E8`, a bare `16px`) instead of a named semantic token.
3. **Component completeness (per component).** Every catalogued component carries **all five**: anatomy (labeled parts), **states** (default/hover/active/focus/disabled/loading/error as applicable), **variants** (type + size), **usage do/don't**, and **accessibility** (role/semantics, keyboard, focus, contrast, state conveyance). *Gap* when any catalogued component is missing one of the five — e.g. variants but no states, or no accessibility line. Missing any of the five fails that component.
4. **Catalog coverage — both floors.** The catalog covers **(a)** every component the product's flows/screens **actually use** — the **hard surface-area floor**, each specced in full — **AND (b)** the common standard component set, **sized to the archetype**. *Gap* when a real screen needs a component the catalog omits or under-specs (a coverage hole), or when the archetype-appropriate standard set is materially incomplete. The hard floor is non-negotiable; the standard set scales with the archetype.
5. **Accessibility standards explicit + numeric.** A stated WCAG conformance target plus concrete, checkable thresholds: text contrast **>=4.5:1** (large text **>=3:1**); non-text/UI contrast **>=3:1**; visible focus indicator **>=3:1**; full keyboard operability; no color-only information; a reduced-motion stance. *Gap* when accessibility is aspirational or non-numeric ("we care about accessibility") with no WCAG target or thresholds — that is not a standard.
6. **Patterns present.** The recurring multi-component scenarios the product's flows need are documented (form validation, empty state, destructive-confirm, loading/skeleton, etc.) — each naming the components/tokens it composes and its rules. *Gap* when a pattern the product's flows clearly need is absent.
7. **Voice/content guidelines present.** Tone, terminology, and component-level copy rules (button = verb-first, error = cause + fix, etc.) are stated. *Gap* when voice/content guidance is absent for a product whose surface area has user-facing copy.
8. **Grounded, not boilerplate.** Tokens and components reflect **this product's** direction (archetype-sized), and genuine gaps are surfaced as **explicit assumptions/open-questions** rather than invented brand answers. *Gap* when the content is generic fill that would be true of any product, or when a missing brand/contrast/convention answer was **fabricated** to look grounded instead of flagged.
9. **Usable downstream.** Wireframing can reference **real** components/tokens by name, and UI engineering can build a consistent, accessible UI, **without asking the author**. *Gap* when an ambiguity, a dangling token reference, or an under-specced component would force a downstream consumer to come back with a question before they can build.

**Proportionality.** "Build a consistent UI from it" scales with the product. A thin product's design system legitimately **collapses sections it does not need** and trims the standard component set to a handful — that is correct sizing, not a gap. Judge **completeness-of-decisions + the surface-area floor**, not row count or word count. A small, complete system that satisfies every *applicable* condition **passes**. Do not manufacture a gap from brevity. (The hard floor in condition 4 still holds at any size: a component a real screen uses must be present and fully specced.)

### Step 3: Decide the verdict

- **approve** — every applicable condition passes. A designer can build a consistent UI and an engineer can implement it from this document as written; the catalog covers the product's surface area. Approve even if you can imagine stylistic improvements; the bar is usability + consistency + accessibility, not perfection — and not maximalism.
- **revise** — one or more conditions have a real, named gap that blocks building a consistent, accessible UI (undefined/inconsistent tokens, a raw value leaking into a component spec, a component missing one of its five parts, non-numeric accessibility, a surface-area coverage hole, fabricated content, etc.).

Do not revise to signal effort or to request nice-to-haves. A condition is either met or it isn't.

### Step 4: Emit the verdict + actionable findings

Emit the verdict as a single line — the literal text `VERDICT: approve` or `VERDICT: revise`, on its own line, with **no** surrounding code fences, quotes, or extra words (the fences here are illustration only):

```
VERDICT: approve
```

Then, on the following lines, list findings. On `revise`, every finding is **actionable** — the failed condition, the exact location, and **how to fix it** — so the author can resolve it in one pass. On `approve`, findings are optional non-blocking notes; do not let them imply a revision is required.

A good finding names the gap and the fix:

> **revise** — Component completeness (cond. 3), "Modal" spec: anatomy, variants, and usage are present but the component lists no states and no accessibility. Fix: add the state set (default/open/closing, focus-trapped) and the accessibility line (role="dialog", focus trap + restore, Esc to close, labelled by the title).

> **revise** — Tokens applied consistently (cond. 2), "Button" spec: `background: #1A73E8` is a raw hex value. Fix: reference the semantic token (e.g. `color.action.primary`) so theming and consistency hold; define that token in the color section if absent.

A bad finding is vague and unactionable:

> The component specs could be more thorough. *(Which component? Which of the five parts? What fixes it?)*

## Rules

**Hard rules (never violate):**

- **Emit exactly one verdict line, `VERDICT: approve` or `VERDICT: revise`** — that literal token, on its own line, nothing else on it. Downstream tooling parses it.
- **Judge, never author.** Return findings; do not rewrite, fix, or fill in the document. The producer revises.
- **Single-sourced bar.** Judge against the nine conditions in Step 2 — the same bar the author produces to. Do not invent extra conditions or apply a stricter private standard.
- **No false-revise.** A system that meets every applicable condition is approved, even a thin one for a small product. Proportional sizing that still covers the surface area is not a defect. Revise only on a real, named gap.
- **No false-approve.** Never approve over a genuine gap to be agreeable. A blocking gap is a `revise`.
- **A raw value in a component spec is a consistency gap.** A component referencing a literal value (hex/HSL/raw px) instead of a named semantic token fails condition 2 — that is the most common consistency failure.
- **A component missing one of its five parts is a gap.** Anatomy + states + variants + usage + accessibility — all five, per component (condition 3).
- **Accessibility must be numeric.** A WCAG target plus concrete thresholds (>=4.5:1 text, >=3:1 large/UI, >=3:1 focus, keyboard, no color-only, reduced-motion). "Accessible" without numbers fails condition 5.
- **The surface-area floor is non-negotiable.** A component a real screen uses, missing or under-specced, is a coverage gap regardless of how complete the standard set looks (condition 4).
- **Fabrication is a gap, not grounding.** An invented brand answer or contrast figure presented as fact fails condition 8 — a real gap should be flagged as an assumption/open-question, not papered over.
- **Judge against the upstreams the document was given.** Assess the document against its `depends_on` set (the upstream documents the project actually produced). A **not-produced** upstream is **never** a revise trigger — never invent an expectation of a document the project didn't make. But a document that **ignored a produced upstream** it should have drawn on (e.g. a `depends_on` feature-spec whose behaviors the flows don't reflect) **is** a fair finding.
- **Every revise finding is actionable** — failed condition + location + concrete fix. No vague notes.

**Preferences (override-able):**

- Order findings by severity — blocking gaps first, then minor ones.
- Reference the condition number/name in each finding so the author maps it back to the bar.
- Keep approve-notes few and clearly non-blocking.

## Gotchas

- **Approving for completeness instead of buildability.** Every section can be present and the UI still un-buildable consistently (raw values in specs, a component missing states/accessibility, non-numeric contrast). Judge whether a designer/engineer can *build a consistent, accessible UI*, not whether the *template is filled*.
- **The raw value hiding in a component spec.** A token section can define `color.action.primary` correctly while a "Button" spec still hard-codes `#1A73E8`. The system reads consistent but isn't — components must reference the **semantic** token, not the value (cond. 2). This is easy to miss when the token tables look right.
- **The half-specced component.** A component with anatomy, variants, and usage but **no states** or **no accessibility** reads complete and can't be built consistently. Presence of *some* parts is not completeness — all five, per component (cond. 3).
- **Catalog-from-the-standard-set-only.** A catalog that lists the generic component set but skips a component a real screen uses leaves a coverage hole (cond. 4a). Walk the flows/screens for the hard floor; the standard set is the *second* floor, not the only one.
- **Aspirational accessibility.** "We value accessibility" or "follows best practices" with no WCAG level and no numeric thresholds is not a standard (cond. 5). Without numbers, nothing is checkable.
- **Rendered-swatch expectation.** Faulting the document for not being a Figma file, or expecting rendered swatches — the artifact is **textual** (values + spec tables). Judge the values on the page, not the absence of pixels.
- **Systematic over-flagging (false-revise).** A reviewer asked to find problems — especially one also asked to propose fixes — tends to over-correct, judging sound systems as defective. Calibrate to the bar: a condition is a gap only on a *named, real* deficiency, not on a token or component you'd have designed differently. Plausible-sounding nits are the dominant reviewer error here.
- **False-revise on a proportionally-sized system.** A thin product's design system is correctly small — a handful of components, collapsed sections it doesn't need. That is right-sizing, not under-specification. Manufacturing a gap from brevity drives avoidable revise loops; calibrate to the archetype and the surface area (cond. 4b is archetype-sized; the hard floor in 4a is what still binds).
- **Confusing this with the wireframe or user-flow gate.** A design system is the reusable *vocabulary* (tokens + component catalog). A wireframe judges where components sit on a screen; a user-flow judges navigation paths. Don't apply a per-screen-layout or a flow-coverage bar to the visual language.
- **Verdict token drift.** "Approved", "LGTM", "needs work", or a verdict buried mid-paragraph will not parse. Emit the literal `VERDICT: approve|revise` on its own line.

## Anti-patterns

- **Rubber-stamp approve.** Skimming and approving to avoid a revise loop — the gate exists to catch systems no one can build a consistent UI from; a raw value in a spec or a component with no accessibility waved through becomes an inconsistent, inaccessible UI or a mid-build clarification scramble.
- **Nit-pick revise.** Blocking on palette taste, naming preference, or nice-to-haves dressed up as gaps. Revise is for real usability/consistency/accessibility blockers only.
- **Silent rewrite.** "It was easier to just fix the token" — authoring inside a review collapses the produce/judge separation and removes the author's chance to learn the gap.
- **Inventing conditions.** Adding a private requirement the bar does not carry ("it should also include dark-mode tokens / a Figma link") drifts the review-bar off the produce-bar and causes spurious revises. Judge the nine conditions only.
- **Maximalism.** Demanding the full broad standard component set from a thin product's system. The bar is the surface-area floor + an archetype-sized standard set, not the largest possible catalog.
- **Hedged verdict.** "Mostly approve but…" or two verdict lines. Exactly one decision, exactly one token.

## Output

A single review result for one design-system document:

- **One verdict line** — `VERDICT: approve` or `VERDICT: revise`, verbatim, on its own line.
- **Findings** — on `revise`, one actionable finding per blocking gap (failed condition + location + concrete fix); on `approve`, optional non-blocking notes.

The abstract consumer is whatever orchestrates the produce->review loop: `approve` accepts the design system for the next phase (wireframing / UI engineering); `revise` returns the findings to the producer for a bounded revision pass.

## Related

- A **design-system-authoring** skill — the produce half of the pair; it writes the document to the same usability + consistency + accessibility bar this skill judges against. Pairing them single-sources the bar so produce and review do not drift.
- A **wireframe-review** skill — the gate for per-screen structural layout (where this system's components are placed on a screen). Distinct doc, distinct bar; this skill judges the reusable visual language one layer up, not any single screen.
- A **user-flow-review** skill — the gate for navigation paths through the product. Distinct doc, distinct bar; not the visual vocabulary.
- A **design-review** skill — the gate for engineering design documents (architecture specs, design docs, ADRs, RFCs), which verifies claims against the codebase. Distinct gate, distinct bar; not for a design-system document.
- A **design-system template / content-template** tool — owns the section *structure*; this skill judges *quality against the bar*, not structural conformance.

## Progressive disclosure

- `references/sources.md` — research provenance for the review method (the single-sourced quality bar, the token-consistency and component-completeness criteria, the WCAG accessibility thresholds, and the reviewer-overcorrection evidence behind the no-false-revise discipline). Load only to audit where the guidance came from.

## Body budget

- `description` <= 1,024 chars (agentskills.io cap). Claude truncates the combined `description` + `when_to_use` at 1,536 chars in the listing.
- Body <= ~500 lines / 5,000 tokens — kept in context every turn.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k tokens, error >50k.
