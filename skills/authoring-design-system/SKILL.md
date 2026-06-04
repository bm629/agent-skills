---
name: authoring-design-system
description: >
  Use when authoring a design-system document — the reusable visual and
  interaction language a product's UI draws on: design principles, design
  tokens (color, typography, spacing, elevation, motion), a component catalog,
  shared patterns, accessibility standards, and voice. Guides the producer
  through the METHOD, not the outline: grounding tokens and components in
  established practice, naming tokens by intent in a primitive/semantic/
  component tiering, sizing the catalog to the product, and specifying each
  component with anatomy + states + variants + usage + accessibility — to a bar
  a designer/engineer can build a consistent, accessible UI from. Composes with
  a separate design-system template tool (section structure) and a
  deep-research capability. Targets a textual markdown artifact (hex/HSL values,
  type-scale + component spec tables), not rendered swatches. Not for reviewing
  a finished design system, not for per-screen layout (that is wireframing),
  and not for a coded component library.
extensions:
  claude:
    when_to_use: "authoring or expanding a design-system document for a product"
    argument-hint: "<the product direction / PRD (and any user-flows) to build a design system for>"
version: "1.1.0"
forge:
  status: reviewed
  forged: 2026-06-04
  reviewed: 2026-06-04
---

# `authoring-design-system` — SKILL.md

> **Variant:** standard · **When to use:** producing a design-system document from a product's direction, to a quality bar a designer/engineer can build a consistent, accessible UI from.

## Overview

This skill is the *how-to* of writing a usable, consistent, accessible design-system document — the reusable visual + interaction language a product's UI draws on (principles, design tokens, a component catalog, patterns, accessibility standards, and voice). It supplies the producer's **judgment**, not the section list. It assumes two collaborators: a **design-system template tool** that supplies the section *structure*, and a **deep-research capability** to ground tokens and components in established practice. The producer is handed the **product direction (and any user-flows)** and must **elaborate** it — never emit generic boilerplate. The bar to clear: a designer can build a consistent UI and an engineer can implement it from the document, and the catalog covers every component the product's screens need. The document is the *vocabulary* later wireframes draw on — it precedes them.

## When to activate

- Authoring a new design-system document from a product's direction / PRD.
- Expanding a thin token set or component list into a full design system (foundations + catalog + patterns + accessibility + voice).
- Filling a design-system template with researched, decision-complete content.

**Do NOT activate when:**

- Reviewing or grading a finished design system → use `reviewing-design-system` (it asserts the same bar this skill produces to).
- Defining per-screen layout / where components are placed → that is `authoring-wireframes`, which *references* the design system this skill produces.
- Shipping a coded component library (CSS/React) → this is the *document* (tokens + specs + rules), not the implementation.
- Authoring a different document type → use that type's skill.

## Inputs

Read **every document the plan hands you** — your `depends_on` set (the upstream documents discovery determined inform this one) — and trace this document's content back to them. Do not assume a fixed input: the typical upstreams this skill names are method guidance, not a cap on what you receive. Be **self-contained** — produce the document from *whatever* context you actually receive; when an expected informing document is absent, proceed on what you have and surface the gap as an explicit assumption, never fabricate to fill it. And **use a research capability where one is available** (deep-research) to make the document comprehensive and exhaustive, not merely to fill the template.

## Workflow

### Step 1: Take the structure from the template tool — don't invent an outline

Get the section structure from your design-system template tool (comprehensive variant). Do **not** restate or re-derive a section list here; this skill supplies the method that *fills* those sections well. If no template is available, obtain a comprehensive design-system structure (request/forge one, or fall back to the canonical set: principles → design tokens → component catalog → patterns → accessibility standards → voice), then proceed.

### Step 2: Load the product direction + surface area; commit to elaborating it

Read the product direction / PRD (personas, the product's purpose and surface area) and any **user-flows** (they signal which screens — and therefore which components — exist). This is the input, never a blank page. **Identify the product archetype** (thin CLI vs. content app vs. a full interactive UI product) — it sizes the whole system. Where the brand or visual direction is thin, make choices **explicit** (a stated Assumption or Open Question), never silently generic.

### Step 3: Research to ground tokens, components, and accessibility

Use a deep-research pass to ground tokens, the component set, patterns, and the accessibility target in **established design-system practice** rather than invent them. Research the conventions you'll instantiate: token tiering and naming, type-scale roles, the standard component set for this archetype, and the current WCAG conformance level. **If no research capability is available, do NOT fabricate** — state the chosen conventions as explicitly-flagged assumptions and proceed against the canonical defaults.

### Step 4: Apply the per-section method

Fill the template's sections to this method:

- **Principles** — 3–6 **opinionated, actionable** beliefs a reviewer could settle a disagreement with, each naming the tradeoff it picks. Not platitudes ("be delightful").
- **Design tokens** — name every design decision as a token, in **three tiers**: *primitive/reference* (raw value) → *semantic/system* (named by **intent**, references a primitive) → *component* (references a semantic). Name by **intent, not appearance** (`color.action.primary`, not `color.blue.500`) — the semantic layer is what components reference, and it is what makes the system *consistent*. Express every value **textually**:
  - **Color** — primitive ramps + semantic role tokens (text / action / feedback / surface / border / focus); record a contrast ratio for every text and UI pairing (ties to accessibility).
  - **Typography** — a role × size **type scale** (the conventional roles are display / headline / title / body / label) as a size / line-height / weight table.
  - **Spacing** — one base unit on a 4px or 8px grid with a multiplicative scale, plus radius/shape tokens; components use tokens, never raw pixels.
  - **Elevation** — a small set of named levels (resting → raised → overlay), each a shadow and/or surface.
  - **Motion** — duration + easing (cubic-bezier) tokens composed into named transitions; include a **reduced-motion** stance.
- **Component catalog** — see Step 5 for sizing; spec **each** component with the same six parts: purpose, **anatomy** (labeled parts + the tokens each uses), **states** (default / hover / active / focus / disabled / loading / error as applicable), **variants** (type + size), **usage do/don't**, **accessibility** (role/semantics, keyboard, focus, contrast, state conveyance).
- **Patterns** — name the recurring multi-component scenario (form validation, empty state, destructive-confirm, …), the components/tokens it composes, and the rules.
- **Accessibility standards** — make targets **numeric and checkable** (see Step 6), not aspirational.
- **Voice & content** — tone, grammar/mechanics, terminology, and component-level copy rules (button = verb-first; error = cause + fix; etc.).
- **Cross-cutting** — every token/component reflects *this* product; surface gaps as explicit assumptions/open-questions; express everything textually (this is a markdown artifact).

### Step 5: Size the component catalog — the hard floor plus the standard set

The catalog must cover **both**:

- **(a) the surface-area hard floor** — every component the product's flows/screens actually use, each specced in full. Walk the user-flows/screens and list the components they imply; none may be missing or under-specified. This is non-negotiable.
- **(b) the common standard component set** — for completeness and reusability, **sized to the archetype** (a thin tool needs a handful; a full UI product needs the broad set: button, link, input, select, checkbox, radio, toggle, badge, avatar, tooltip, card, alert, toast, modal, popover, menu, tabs, accordion, breadcrumb, pagination, table, list, form, navigation, progress, …).

Where a needed component can't be fully specced from the available direction, surface it as an Open Question — don't invent its behavior.

### Step 6: Self-check against the usability/consistency/accessibility bar before handing off

Confirm all hold (this is the bar a reviewer will assert):

1. **Principles stated** — 3–6 actionable principles present.
2. **Tokens defined + applied consistently** — color (incl. semantic roles), typography scale, spacing, elevation, motion all defined as named tokens with concrete values; components reference **semantic tokens**, not raw values.
3. **Component completeness** — every catalogued component carries **anatomy + states + variants + usage do/don't + accessibility**. Missing any of the five fails.
4. **Catalog coverage (both floors)** — covers every component the product's screens use (the hard floor, fully specced) **and** the archetype-sized standard set.
5. **Accessibility standards explicit + numeric** — a stated WCAG target; text contrast ≥ **4.5:1** (large text ≥ **3:1**); non-text/UI contrast ≥ **3:1**; visible focus ≥ **3:1**; full keyboard operability; no color-only information; reduced-motion honored.
6. **Patterns present** — the recurring multi-component scenarios the flows need.
7. **Voice/content guidelines present** — tone + component copy rules.
8. **Grounded, not boilerplate** — tokens/components reflect the product's direction (archetype-sized), with gaps surfaced as assumptions/open-questions.
9. **Usable downstream** — later wireframes can reference real components/tokens, and UI engineering can build a consistent UI, without asking the author.

**Thin-direction gate:** if the product's surface area can't be inferred even approximately (no flows, no screen list, no archetype), surface that as a **blocker** ("direction too thin to scope a catalog — needs the product surface area") rather than inventing a catalog.

## Rules

**Hard rules (never violate):**

- **Compose, don't duplicate.** Take the section structure from the template tool; this skill is the method that fills it. Do not paste a competing outline.
- **Name tokens by intent.** Semantic tokens are named for what they mean (`color.feedback.danger`), never their value (`color.red.600`); components reference semantic tokens, never raw values. This is the consistency guarantee.
- **Every component is fully specced.** A component without anatomy, states, variants, usage do/don't, **and** accessibility is not done.
- **Cover the surface-area floor.** Every component the product's screens use must be in the catalog, fully specced. A real screen needing an undocumented component is a coverage gap, not an acceptable omission.
- **Accessibility is numeric.** State a WCAG target and concrete thresholds (≥4.5:1 text, ≥3:1 large/UI, ≥3:1 focus, keyboard-operable, no color-only). "Accessible" without numbers is not a standard.
- **Never fabricate.** Don't invent a brand palette, a contrast figure, or a convention to look grounded. If unresearched/unknown, state it as an explicitly-flagged assumption.
- **Textual medium.** Express tokens and components as values + spec tables (hex/HSL, type-scale tables, component tables) — this is a markdown document, not a rendered design file.
- **Elaborate the given direction.** Specifics come from the product direction + research, never generic boilerplate.
- **Buildable or not done.** Don't hand off a design system a designer/engineer can't build a consistent, accessible UI from.

**Preferences (override-able):**

- "Comprehensive" sets the output *ambition*, but stay **proportional** — completeness of decisions, not row count. A thin product legitimately collapses sections and trims the standard set it doesn't need (the hard floor still holds).
- Keep principles to 3–6 crisp, actionable bullets.
- Prefer the conventional token tiers and type-scale roles over a bespoke taxonomy unless the product needs otherwise.

## Gotchas

- **Value-named tokens.** `color.blue.500` referenced directly by a button looks fine but kills theming and drifts — name semantically (`color.action.primary`) and reference that. Raw values leaking into component specs is the most common consistency failure.
- **Half-specced components.** A component with variants but no states (or no accessibility) reads complete but can't be built consistently — every component needs all six parts.
- **Catalog from the standard set only.** Listing the generic component set while skipping a component a real screen uses leaves a coverage hole. Walk the flows first (the hard floor), then add the standard set.
- **Aspirational accessibility.** "We care about accessibility" is not a standard. Without numeric thresholds and a WCAG target, nothing is checkable.
- **Rendered-swatch assumption.** Treating this as a Figma file and gesturing at "the blue" instead of writing `#1A73E8` / a contrast ratio. The artifact is textual — values must be on the page.
- **Generic fill.** Tokens/components that would be true of any product means you elaborated the *template*, not the *product*. Tie the palette, the type scale, and the catalog to this product's direction and archetype.

## Anti-patterns

- **"I'll write the outline myself."** Duplicates the template tool — take the structure from it; supply method + bar.
- **"Accessibility is a later pass."** The token and component specs *are* where contrast, focus, and keyboard live — bake them in, don't defer.
- **"The standard component set is the catalog."** It's half the catalog; the other half is every component the product's own screens use, fully specced.
- **"Skip the research, I know design systems."** The research grounds *this product's* tokens/components and the *current* WCAG level — not design-system theory.
- **"It should look clean and modern."** Vague adjectives masquerading as principles or tokens — replace with concrete decisions (named tokens, stated principles) or cut them.
- **"The direction is thin, so I'll invent a full catalog."** Surface the missing surface area as a blocker/open-question instead of fabricating components.

## Output

A **design-system document** that meets the **Step 6 bar** (principles stated; tokens defined + consistently applied; every component fully specced; catalog covering the surface-area floor + the standard set; numeric accessibility standards; patterns; voice; grounded-not-boilerplate; buildable downstream). The **abstract consumer** is downstream wireframing (which references its components/tokens), UI engineering (which builds from it), and a reviewer (which asserts the same bar). The document's *structure* comes from the template tool; this skill supplies the *content quality*. It is expressed textually (markdown) and **precedes** wireframes one-directionally.

## Related

- A **design-system template tool** (e.g. a content/template gateway) — supplies the comprehensive design-system section structure this skill fills.
- A **deep-research capability** — grounds tokens, components, patterns, and the accessibility target in established practice.
- `reviewing-design-system` — asserts the same usability/consistency/accessibility bar on the finished document; author and reviewer share one bar so they don't drift.
- `authoring-wireframes` — the **downstream** consumer: screens place this document's components and reference its tokens. Wireframes depend on the design system; the design system does not depend on wireframes.
- The upstream **product-direction / PRD** (and optionally **user-flows**) — the input context this skill elaborates; never a blank page.

## Progressive disclosure

- `references/sources.md` — research provenance for the method, the token/component conventions, and the accessibility thresholds (load only to audit where the guidance came from).

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap).
- Body ≤ ~500 lines / 5,000 tokens.
- Heavy content lives in `references/`, loaded on demand.
