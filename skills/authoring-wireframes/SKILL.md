---
name: authoring-wireframes
description: >
  Use when authoring or amending a wireframes document — the low-to-mid-fidelity
  STRUCTURAL design of each key screen (layout regions on a grid + shared
  app-shell, content hierarchy, components, affordances, content/microcopy intent,
  the per-screen empty/loading/populated/error/success states, screen-composition
  accessibility), as a textual/annotated wireframe (ASCII sketch + annotations),
  NOT a pixel mockup. Guides the METHOD, not the outline: deriving the screen list
  from the upstream user-flows (one wireframe per flow-named screen/state),
  composing each screen to an objective layout-quality bar, grounding it in
  established UI patterns, referencing a design-system's real components, owning
  screen-composition a11y (design-system owns the per-component contract), and
  amending as a scoped versioned delta — to a bar an engineer can build the screen
  structure from. Composes with a template tool + research. Not for reviewing a
  wireframes doc, hi-fi visual design, the navigation graph (user-flows), or other
  types.
extensions:
  claude:
    when_to_use: "authoring or amending a wireframes document from the upstream user-flows"
    argument-hint: "<the project idea + the upstream user-flows (and design-system if any) to lay out as screens>"
version: "1.2.0"
forge:
  status: reviewed
  forged: 2026-06-04
  reviewed: 2026-06-14
---

# `authoring-wireframes` — SKILL.md

> **Variant:** standard · **When to use:** producing (or amending) a structural wireframes document from the upstream user-flows, to a bar an engineer can build the screen structure from.

## Overview

This skill is the *how-to* of writing a strong, comprehensive **wireframes** document — the judgment a producer applies, not the section list. A wireframe here is **low-to-mid fidelity and structural**: the layout regions (on a grid, in a shared app-shell), content hierarchy, components, affordances, content/microcopy intent, per-screen states, and screen-composition accessibility of each key screen — expressed in text as a **structured layout description + an ASCII/markdown box sketch + per-element annotations**, not a pixel mockup. It assumes two collaborators: a **template tool** that supplies the section *structure*, and a **deep-research capability** to ground each screen in established UI patterns. The producer is handed the **upstream user-flows** (the screens and state-transitions each flow traverses) plus a **design-system** if one exists — and lays out every flow-named screen, never a blank page. The bar to clear: the doc is *buildable* (an engineer can build the screen structure), *covered* (every flow-named screen + state has a wireframe), and *well-composed* (an objective layout-quality bar).

Fidelity is a spectrum across three axes — **interactivity, visuals, content** (NN/g). A wireframe is low-to-mid on visuals, mid on structure, low on interactivity. **Final color/type/pixels are downstream hi-fi; the token system + per-component a11y contract are the design-system's** — this skill stays structural. The method is **medium-independent**: the artifact today is markdown; a future design-tool backend changes only the medium, not the thinking or the bar.

## When to activate

- Authoring a new wireframes document from a project idea + the upstream user-flows.
- Laying out the key screens (and their states) that a set of user-flows names.
- **Amending** an existing wireframes doc when a flow, screen, region, or referenced component changes (see Step 8).
- Filling a wireframes template with researched, decision-complete structural content.

**Do NOT activate when:**

- Reviewing or grading a finished wireframes doc → use `reviewing-wireframes`.
- Producing high-fidelity visual design / final pixels / color + type / motion → that is the downstream **hi-fi** pass; the design-system owns the visual tokens.
- Re-deciding which screens and transitions exist → that is the upstream **user-flows**; this lays out each screen.
- Authoring or grading the token system / component catalog → that is the **design-system**.
- Authoring a different document type → use that type's skill.

## Inputs

Read **every document the plan hands you** — your `depends_on` set (the typical upstreams: the **user-flows** that name the screens, and a **design-system** where one exists). Trace this document's content back to them. Do not assume a fixed input: the named upstreams are guidance, not a precondition. Be **self-contained** — produce from *whatever* context you receive; when an expected upstream is absent, proceed on what you have and surface the gap as an explicit assumption (Step 7), never fabricate. **Use a research capability** (deep-research) where available to ground each screen, not merely to fill the template.

## Workflow

### Step 1: Take the structure from the template tool — don't invent an outline

Get the section structure from your wireframes template tool (comprehensive variant). Do **not** restate a section list here; this skill supplies the method that *fills* those sections well. If no template is available, obtain/forge a comprehensive wireframes structure, then proceed.

### Step 2: Derive the screen list from the upstream user-flows

The wireframes doc **`depends_on` the user-flows**. Walk every flow; **every screen a flow names, and every state-transition it implies, gets a wireframe.** Build a **screen-inventory table** (each flow-named screen/state → its wireframe section + the states it visits) so coverage is auditable — this table is also the amend-ripple surface (Step 8). A flow naming a screen with **no defined content** is a gap — record it (Step 7), never silently invent it.

### Step 3: Research to ground each screen — don't invent patterns; hold the fidelity line

Use deep-research to ground each screen in **established UI patterns** (conventional layouts for its type — list/detail, master-detail, dashboard, settings, wizard, auth, search-results — and standard empty/loading/error treatments) rather than inventing structure. Where a **design-system** exists, reference its **real components and tokens** — never invent them. Hold the **fidelity line**: lay out *structure* (regions, grid intent, component selection, affordances, states), never exact hex/px/type — that is hi-fi overshoot. If no research capability is available, don't fabricate a pattern or a component name — lay out the conventional structure and flag uncertainty as an assumption.

### Step 4: Establish the global frame — grid, app-shell, layout-quality bar

Before the per-screen work, fix the conventions every screen inherits:

- **Layout grid + spacing cadence (structure, not pixels):** the column structure (e.g. 12-col) + an 8pt (or 4pt dense) rhythm *intent*. State the cadence; the design-system owns exact px. A raw `13px` is off-cadence and a hi-fi overshoot.
- **App-shell / page-frame:** ONE shared header/nav/container/max-width, defined once and reused on every screen — no per-screen full-bleed dumps. This shared region is what an amend ripples through.
- **Objective layout-quality bar** (every screen composes to it; subjective taste is NOT required): primary action on the scan path (F/Z), related elements grouped (Gestalt proximity), no gratuitous region/element, consistency across sibling screens.

### Step 5: Apply the per-screen method

Fill the template's per-screen sections to this method. For **each** key screen:

- **Purpose & flow context** — one sentence on what the screen lets the user do, the flow step it serves, entry points + where each affordance exits.
- **Layout regions + content hierarchy** — name the regions (Step-4 vocabulary) and their arrangement on the grid; order content by visual priority driven by the primary task; group related items (Gestalt) and place the primary action on the scan path. Structure before any visual concern.
- **Box sketch** — an ASCII/markdown sketch of the default/populated layout: regions labelled, key elements placed, the legend defined once and reused. Keep the sketch and its annotations **in sync**.
- **Components & affordances (annotations)** — per notable element: the **design-system component** (or a generic type), full anatomy where it applies, its behavior on interaction (tap/hover/validation/conditional visibility), where it leads, and edge cases (truncation/overflow/sort/paginate/dropdown). Annotations turn a static layout into a buildable spec.
- **Data-display** *(for data-dense screens)* — table vs list vs cards; for a table: columns + sort/filter/paginate/row-density/sticky-header/row-expansion; **progressive disclosure** (what's primary vs deferred behind accordion/disclosure/tooltip/show-more); **forms** with grouped fields + structured inputs (no hand-authored serialized strings).
- **Content & microcopy (intent, not final copy)** — the *intent* of each text slot (label/heading/button/empty/error/placeholder); **speak the user's language** (no raw data-model identifier as a label — human label + one-line description); **placeholder ≠ label**; **terminology consistency** (one name per concept across screens); **i18n** text-expansion room + RTL where localized (scope out single-locale with a one-line reason).
- **Per-screen states** — **empty** (why + guide-to-action CTA, plain language), **loading** (a skeleton mirroring the populated layout over a bare spinner where the layout is known), **populated/default**, **error** (plain-language cause + recovery + placement, inline vs blocking, no raw codes), **success/confirmation** (what changed + next step) and **partial** where the path visits them. Trace the states to the ones the flow's path actually visits. Happy-path-only is the #1 gap.
- **Responsive notes** *(where form-factor matters)* — what stacks/collapses (nav → hamburger/off-canvas)/hides/reorders and the *mechanism*; content-priority change on small screens (promote/demote/hide, not just stack); touch-target reservation.
- **Accessibility — screen-composition** — landmarks per region, one-h1 heading order, reading/focus order (incl. on conditional reveal), accessible names for icon-only controls, keyboard operability (no mouse-only step), **target-size reservation** (≥24×24 CSS px; SC 2.5.8), **focus-not-obscured** by sticky regions (SC 2.4.11), non-color-only intent (SC 1.4.1). **Defer pixel contrast + focus-appearance to the design-system** (the per-component contract); if no DS/hi-fi exists downstream, record that deferral as an assumption (Step 7), don't drop it.

### Step 6: Self-check against the bar before handing off

Confirm all hold (this is the bar `reviewing-wireframes` asserts — same list, single-sourced, each proportional to the screen's archetype):

1. **Full coverage** — every flow-named screen + state-transition has a wireframe (no orphans/gaps vs the flows).
2. **All applicable states** — empty/loading/populated/error + success where a state-change occurs + partial where relevant; *quality*, not just presence.
3. **Layout & composition** — regions + hierarchy unambiguous; on a grid; in the shared app-shell; the **objective layout-quality bar** met (scan-path/grouping/no-gratuitous/sibling-consistency).
4. **Components** — DS components named + consistent + composed; none invented.
5. **Affordances + data-display** — behaviors/destinations annotated; data-dense screens specify their table/disclosure/form structure.
6. **Content & microcopy** — text-slot intent stated; no data-model leak in labels; persistent labels; consistent terminology.
7. **Responsive** — reflow mechanism + mobile priority where form-factor matters.
8. **Screen-composition a11y** — landmarks/one-h1/reading order/names/keyboard/target-reservation/focus-not-obscured/non-color (pixel-contrast deferred to the DS).
9. **Annotation & handoff** — legend defined; sketch ⇄ annotations in sync; elements map to DS components (the handoff translation).
10. **Gaps surfaced** — undefined screens/content, missing components, deferred component a11y = explicit assumptions/open-questions.
11. **Structural, not hi-fi** — lo-to-mid fidelity; no final pixels/color/type.
12. **Versioned (on amend)** — the doc's own version + changelog reflect the change (Step 8).

### Step 7: Surface gaps explicitly

A flow naming a screen with undefined content, an element needing a component the design-system doesn't define, or component-contract a11y with no DS/hi-fi downstream → an **open question or assumption**. List it; flag missing components for the design-system owner. Never paper a gap with an invented screen/component.

### Step 8: Amend mode — edit, don't redraw (when iterating)

When handed an existing wireframes doc + a change, treat it as a **scoped, versioned diff**, never a regenerate:

1. **Scope + ripple** — identify which screen(s)/state(s)/region(s) change, then trace the ripple: every screen reusing a **changed shared region** (app-shell/nav/header), every inventory row / flow hand-off referencing an edited/removed screen, every screen naming a **changed/deprecated DS component**, every screen added/removed by an upstream **flow** change.
2. **Edit, don't redraw** — minimal in-place edit; untouched screens stay byte-for-byte unchanged; a **shared-region change is applied to ALL reusing screens in one pass** (the one legitimate wide ripple), not screen-by-screen drift; stable screen + component names preserved.
3. **Version + changelog** — bump the **doc's own** version: MAJOR (removed/renamed screen or removed state — breaks the build/hi-fi contract), MINOR (added screen/state/region/component), PATCH (annotation/notation/copy-intent fix); add a Keep-a-Changelog entry at the screen/state grain.
4. **Deprecate before removing** — mark a screen/state deprecated in a MINOR (note the replacement) before removing in a MAJOR; on removal confirm no inventory row / flow hand-off still references it and prune the inventory.

## Rules

**Hard rules (never violate):**

- **One wireframe per flow-named screen/state.** Coverage is keyed to the upstream user-flows; an orphan screen or missing state is incomplete.
- **All applicable states.** empty/loading/populated/error + success on a state-change. Happy-path-only is not done. A truly static screen collapses inapplicable states (proportional).
- **Reference real components; never invent.** Name the design-system's real components/tokens; a custom need is a flagged gap, not a silent invention.
- **Structural, not hi-fi.** Layout + hierarchy + annotation; no final pixels, color, or type — that is the hi-fi pass; the design-system owns tokens.
- **Own composition a11y; defer the component contract.** The wireframe owns landmarks/heading/focus-order/names/keyboard/target-reservation/focus-not-obscured/non-color; the design-system owns pixel contrast + focus-appearance + the component's own target-size/keyboard. Don't re-judge what the DS certifies; don't drop it when no DS exists (assumption instead).
- **Speak the user's language.** No raw data-model identifier as a visible label; a placeholder is not a label.
- **One app-shell, on a grid.** Every screen sits in the one shared shell on the grid cadence — no per-screen re-invention.
- **Compose, don't duplicate.** Take the section structure from the template tool; don't paste a competing outline.
- **Lay out the given flows.** The screen set comes from the user-flows, not imagination; don't re-decide navigation.
- **Surface gaps, don't invent.** Undefined screen/content, missing component, deferred a11y = explicit assumption/open-question.
- **Amend, don't regenerate.** On iteration, edit in place + version + changelog; never re-draw untouched screens.
- **Buildable or not done.** Don't hand off a doc an engineer cannot build the screen structure from.

**Preferences (override-able):**

- "Comprehensive" sets *ambition*, but stay **proportional** — completeness-of-decisions for the screen's archetype, not word count. A trivial screen collapses sections it doesn't need.
- Define the ASCII notation legend once per doc and reuse it.
- Prefer a skeleton-that-mirrors-the-populated-layout over a bare spinner where the layout is known.
- The objective layout-quality bar is objective only — don't impose subjective layout taste.

## Gotchas

- **Happy-path-only screens.** Omitting empty/loading/error/success is the single most common gap — the states are where real UX lives.
- **Invented components.** Naming a component/token the design-system doesn't define drifts from the system and breaks handoff. Reference real components or flag the gap.
- **Coverage gap vs the flows.** A flow names a screen that never gets a wireframe — the inventory table exists to catch exactly this.
- **Drifting into hi-fi.** Exact colors, type, pixel spacing overshoot the structural scope and step on the hi-fi/design-system scope. Stay structural.
- **Double-judging a11y.** Re-specifying pixel contrast/focus-appearance the design-system owns is drift, not rigor — own composition a11y, defer the component contract.
- **Data-model leaking into labels.** A raw identifier (`manifest_docs`) as a visible label is the schema leaking through — translate to a human label + description.
- **Generic fill.** A layout that fits any product means you laid out the *template*, not *this product's flow*. Tie every screen to its flow step + real content.
- **Static layout, no annotations.** A box sketch with no per-element annotation is a picture, not a spec. Annotate components, affordances, states — and keep them in sync with the sketch.
- **Shared-region drift on amend.** Editing the app-shell on one screen but not the others that reuse it is the most common amend regression — apply it to all reusing screens in one pass.

## Anti-patterns

- **"The populated view is enough."** Omits empty/loading/error/success — document all applicable states.
- **"I'll make up a component for this."** Reference the design-system's real ones or flag the gap.
- **"I'll redesign which screens exist."** That re-decides navigation (user-flows' job) — lay out the given screens.
- **"I'll write the outline myself."** Duplicates the template tool — take the structure from it.
- **"Let me add colors and exact spacing to make it concrete."** Overshoots into hi-fi — stay structural.
- **"I'll also pin the exact contrast ratio."** That is the design-system's component contract — reserve non-color intent, defer the pixel value.
- **"The flow is vague here, so I'll invent a plausible screen."** Surface it as an assumption instead.
- **"It's a small change, I'll just regenerate the doc."** Amend in place + version + changelog; never re-draw untouched screens.

## Output

A **comprehensive, structural wireframes document** that meets the **Step 6 bar** (full coverage vs the flows; all applicable states; unambiguous layout/hierarchy on a grid + shared app-shell to the objective layout-quality bar; identified + consistent components; annotated affordances + data-display; content/microcopy intent; responsive where it matters; screen-composition a11y; legend + sketch⇄annotation sync + design-to-code mapping; gaps surfaced; structural-not-hi-fi; versioned on amend). Each screen is a structured layout description + an ASCII/markdown box sketch + per-element annotations. The **abstract consumer** is the downstream hi-fi pass + UI engineering (which build the screen structure) and a reviewer (which asserts the same bar). The doc's *structure* comes from the template tool; this skill supplies the *content quality*.

## Related

- A **wireframes template tool** (e.g. a content/template gateway) — supplies the comprehensive per-screen section structure this skill fills.
- A **deep-research capability** — grounds each screen in established UI patterns and (where present) the design-system's real components.
- **`reviewing-wireframes`** — asserts the same buildability + coverage + composition + layout-quality bar; author and reviewer share one bar so they don't drift.
- The **upstream user-flows** (a `depends_on` document) — names which screens and state-transitions need wireframes.
- A **design-system** (where one exists) — supplies the real components/tokens to reference and owns the per-component a11y contract (contrast, focus-appearance); the wireframe references + reserves, never re-defines.
- The downstream **hi-fi** pass — owns final visuals/pixels; this skill stops at structure.

## Progressive disclosure

- `references/composition-and-states.md` — depth on the grid/8pt cadence, app-shell, Gestalt/scanning hierarchy, the data-display (table/disclosure/form) catalog, and the per-screen state-quality rules. Load when composing a data-dense screen.
- `references/a11y-and-amend.md` — depth on screen-composition WCAG 2.2 (SC 2.5.8 / 2.4.11 / 2.4.3 / 4.1.2 / 1.4.1, the component-contract boundary) + the amend ripple/versioning procedure. Load for an a11y pass or an amend.
- `references/sources.md` — research provenance for the method + the bar (load only to audit where the guidance came from).

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap).
- Body ≤ ~500 lines / 5,000 tokens.
- Heavy content lives in `references/`, loaded on demand.
