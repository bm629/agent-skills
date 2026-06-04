---
name: authoring-wireframes
description: >
  Use when authoring a wireframes document — the low-to-mid-fidelity STRUCTURAL
  design of each key screen (layout regions, content hierarchy, components,
  navigation affordances, and the per-screen empty/loading/populated/error
  states), as a textual/annotated wireframe (layout description + ASCII/markdown
  box sketch + per-element annotations), NOT a pixel mockup. Guides the producer
  through the METHOD, not the outline: deriving the screen list from the upstream
  user-flows (one wireframe per flow-named screen/state), grounding each screen
  in established UI patterns rather than inventing them, referencing a
  design-system's real components where one exists, and surfacing gaps as
  assumptions — to a bar an engineer can build the screen structure from.
  Composes with a separate template tool and a deep-research capability. Assumes
  the upstream user-flows as input — never a blank page. Not for reviewing a
  finished wireframes doc, not for high-fidelity visual design, and not for
  other document types.
extensions:
  claude:
    when_to_use: "authoring a wireframes document from the upstream user-flows"
    argument-hint: "<the project idea + the upstream user-flows to lay out as screens>"
version: "1.0.0"
forge:
  status: reviewed
  forged: 2026-06-04
  reviewed: 2026-06-04
---

# `authoring-wireframes` — SKILL.md

> **Variant:** standard · **When to use:** producing a structural wireframes document from the upstream user-flows, to a bar an engineer can build the screen structure from.

## Overview

This skill is the *how-to* of writing a strong, comprehensive **wireframes** document — the judgment a producer applies, not the section list. A wireframe here is **low-to-mid fidelity and structural**: the layout regions, content hierarchy, components, navigation affordances, and the per-screen states of each key screen — expressed in text as a **structured layout description + an ASCII/markdown box sketch + per-element annotations**, not a pixel mockup (final color, type, and visuals are downstream visual design). It assumes two collaborators: a **template tool** that supplies the section *structure*, and a **deep-research capability** to ground each screen in established UI patterns. The producer is handed the **upstream user-flows** (the screens and state-transitions each flow traverses) plus a **design-system** if one exists — and must lay out every flow-named screen, never a blank page. The bar to clear: the doc is *buildable* — an engineer can build the screen structure and every flow-named screen + state has a wireframe.

The method is **medium-independent**. The artifact today is markdown (layout description + ASCII sketch + annotations); a future design-tool backend changes only the medium, not the structural thinking or the bar below.

## When to activate

- ✅ Authoring a new wireframes document from a project idea + the upstream user-flows.
- ✅ Laying out the key screens (and their states) that a set of user-flows names.
- ✅ Filling a wireframes template with researched, decision-complete structural content.

**Do NOT activate when:**

- Reviewing or grading a finished wireframes doc → use a wireframes-review skill.
- Producing high-fidelity visual design / final pixels / color + type → that is downstream visual design; the design-system owns the visual tokens.
- Re-deciding which screens and transitions exist → that is the upstream user-flows; this lays out each screen.
- Authoring a different document type → use that type's skill.

## Workflow

### Step 1: Take the structure from the template tool — don't invent an outline

Get the section structure from your wireframes template tool (comprehensive variant). Do **not** restate or re-derive a section list here; this skill supplies the method that *fills* those sections well. If no template is available, obtain a comprehensive wireframes structure (request/forge one, or fall back to the canonical per-screen section set), then proceed.

### Step 2: Derive the screen list from the upstream user-flows

The wireframes doc **`depends_on` the user-flows** — they are its input, not a blank page. Walk every flow; **every screen a flow names, and every state-transition it implies, gets a wireframe.** Build a **screen inventory** (a table mapping each flow-named screen/state to its wireframe section) so coverage is auditable. A flow that names a screen with **no defined content** is a gap — record it as an explicit assumption or open question (Step 6), never silently invent it.

### Step 3: Research to ground each screen — don't invent patterns

Use a deep-research pass to ground each screen in **established UI patterns** (conventional layouts for this screen type, standard empty/loading/error treatments) rather than inventing structure. Where a **design-system** exists, reference its **real components and tokens** — never invent component names or visual tokens (the design-system owns those). Research the specific domain of the screens, not "wireframing in general." If no research capability is available, do **not** fabricate a pattern or a component name — lay out the conventional structure and flag any uncertain component as an assumption to validate.

### Step 4: Apply the per-screen method

Fill the template's per-screen sections to this method. For **each** key screen:

- **Purpose & flow context** — one sentence on what the screen lets the user do, and the flow step it serves (entry points + where each affordance exits).
- **Layout regions** — name the regions (header, nav, content, sidebar, footer as the product uses them) and their arrangement. Establish structure **before** any visual concern — a wrong structure is the failure wireframes exist to catch.
- **Content hierarchy** — order content by visual priority (most important first), driven by the screen's primary task.
- **Box sketch** — an ASCII/markdown sketch of the default/populated layout: regions labelled, key elements placed. Define a notation legend once for the doc (e.g. `[ Button ]`, `_____` input, `▢`/X media, `>` affordance).
- **Components & affordances (per-element annotations)** — per notable element: the component (the design-system component where one exists, else a generic type), its behavior on interaction (tap/hover/validation/conditional visibility), where the affordance leads, and edge cases (truncation, overflow, sorting, pagination, dropdown contents). Annotations are what turn a static layout into a buildable spec.
- **Per-screen states** — document **all four**: empty (why empty + the CTA to create/find content), loading (skeleton mirroring the populated layout, or the indicator + what's blocked), populated/default (the normal filled view), error (message placement, what's recoverable, the retry/next affordance, inline vs blocking). Happy-path-only is the most common gap.
- **Responsive notes** — how the screen reflows across the target breakpoints: what stacks, collapses (nav → hamburger), hides, or reorders, and any content-priority change on small screens. State the *how* of the transition, not just *what* changes.
- **Accessibility notes** — focus/reading order, ARIA landmarks per region, accessible names for unlabeled controls, heading levels (one h1/screen), and contrast / non-color-only intent. Communicate intent at handoff; it does not replace testing.

### Step 5: Self-check against the buildability bar before handing off

Confirm all hold (this is the bar a reviewer will assert — same list, no drift):

1. **Full screen coverage** — every screen the user-flows name (and every implied state-transition) has a wireframe. No orphans, no gaps vs the flows.
2. **All four states per screen** — empty, loading, populated, error each documented.
3. **Unambiguous layout + hierarchy** — clear enough to build the structure without guessing.
4. **Components identified + consistent** — each notable element names its component (design-system where one exists); reused components are consistent across screens; no invented components/tokens.
5. **Affordances annotated** — every interactive element's behavior and destination, including relevant edge cases.
6. **Responsive considered** — reflow stated where it matters.
7. **Accessibility considered** — focus order, labels/landmarks, contrast/non-color intent annotated.
8. **Gaps surfaced** — undefined screens/content and missing design-system components are explicit assumptions/open-questions, not silently filled.
9. **Structural, not hi-fi** — stays lo-to-mid fidelity (layout + annotation); no final pixels/color/type.

### Step 6: Surface gaps explicitly

A flow that names a screen with undefined content, or an element that needs a component the design-system does not yet define, is an **open question or assumption** — list it; flag missing components for the design-system owner. Never paper a gap with an invented screen or component.

## Rules

**Hard rules (never violate):**

- **One wireframe per flow-named screen/state.** Coverage is keyed to the upstream user-flows; an orphan screen or a missing state is incomplete.
- **All four states.** Every screen documents empty, loading, populated, and error. A happy-path-only screen is not done.
- **Reference real components; never invent.** Where a design-system exists, name its real components/tokens. Don't invent component names or visual tokens — the design-system owns them.
- **Structural, not hi-fi.** Stay low-to-mid fidelity: layout + hierarchy + annotation. No final pixels, color, or type — that is downstream visual design.
- **Compose, don't duplicate.** Take the section structure from the template tool; this skill is the method that fills it. Do not paste a competing outline.
- **Lay out the given flows.** The screen set comes from the upstream user-flows, not from imagination. Don't re-decide the navigation.
- **Surface gaps, don't invent.** An undefined screen/content or a missing component is an explicit assumption/open-question, never silently filled.
- **Buildable or not done.** Don't hand off a wireframes doc an engineer cannot build the screen structure from.

**Preferences (override-able):**

- "Comprehensive" sets the output *ambition*, but stay **proportional** — completeness of decisions (every flow-named screen + four states, layout/hierarchy/components/affordances/a11y covered), not word count. A trivial screen legitimately collapses sections it doesn't need.
- Define the ASCII notation legend once per doc and reuse it.
- Prefer a skeleton-that-mirrors-the-populated-layout for the loading state over a bare spinner where the layout is known.

## Gotchas

- **Happy-path-only screens.** Documenting only the populated view and omitting empty/loading/error is the single most common wireframe gap — the states are where real UX lives.
- **Invented components.** Naming a component the design-system doesn't define (or inventing visual tokens) drifts from the system and breaks handoff. Reference real components or flag the gap.
- **Coverage gap vs the flows.** A flow names a screen that never gets a wireframe — the inventory table exists to catch exactly this. Trace flows → screens before claiming done.
- **Drifting into hi-fi.** Specifying exact colors, type, spacing, or pixel-perfect layout overshoots the structural scope and steps on the design-system's tokens. Stay structural.
- **Generic fill.** A screen layout that would fit any product means you laid out the *template*, not *this product's flow*. Tie every screen to the flow step it serves and the real content it holds.
- **Static layout, no annotations.** A box sketch with no per-element annotation is a picture, not a spec — a developer still has to guess behavior. Annotate components, affordances, and states.

## Anti-patterns

- **"The populated view is enough."** Omits empty/loading/error — forbidden; document all four states per screen.
- **"I'll make up a component for this."** Inventing components/tokens — reference the design-system's real ones or flag the gap.
- **"I'll redesign which screens exist."** That re-decides the navigation — the screens come from the upstream user-flows; lay them out, don't re-author them.
- **"I'll write the outline myself."** Duplicates the template tool — take the structure from it.
- **"Let me add colors and exact spacing to make it concrete."** Overshoots into hi-fi visual design — stay structural; the design-system owns visuals.
- **"The flow is vague here, so I'll invent a plausible screen."** Surface it as an assumption/open-question instead; never silently invent.

## Output

A **comprehensive, structural wireframes document** that meets the **Step 5 buildability bar** (full screen coverage vs the flows, all four states per screen, unambiguous layout + hierarchy, identified + consistent components, annotated affordances, responsive + accessibility considered, gaps surfaced, structural-not-hi-fi). Each screen is a structured layout description + an ASCII/markdown box sketch + per-element annotations. The **abstract consumer** is downstream visual design + UI engineering (which build the screen structure from it) and a reviewer (which asserts the same bar). The doc's *structure* comes from the template tool; this skill supplies the *content quality*.

## Related

- A **wireframes template tool** (e.g. a content/template gateway) — supplies the comprehensive per-screen section structure this skill fills.
- A **deep-research capability** — grounds each screen in established UI patterns and (where present) the design-system's real components.
- A **wireframes-review skill** — asserts the same buildability bar on the finished doc; author and reviewer share one bar so they don't drift.
- The **upstream user-flows** (a `depends_on` document) — the input that names which screens and state-transitions need wireframes.
- A **design-system** (where one exists) — supplies the real components/tokens to reference instead of inventing them.

## Progressive disclosure

- `references/sources.md` — research provenance for the method + quality bar (load only to audit where the guidance came from).

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap).
- Body ≤ ~500 lines / 5,000 tokens.
- Heavy content lives in `references/`, loaded on demand.
