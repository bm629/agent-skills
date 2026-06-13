---
name: authoring-design-system
description: >
  Use when authoring a design-system document — the reusable visual + interaction
  language a product's UI draws on: principles, design tokens (color incl. modern
  color spaces, typography, spacing, elevation, motion, iconography) in the W3C
  DTCG format, a component catalog, patterns, layout + internationalization
  conventions, WCAG 2.2 AA accessibility, voice, and lifecycle/governance. Guides
  the METHOD, not the outline: grounding tokens/components in established practice,
  naming tokens by intent in a primitive/semantic/component tiering, theming via
  alias-swap (light/dark + multi-brand), sizing the catalog to the archetype,
  specifying each component with anatomy + states + variants + usage +
  accessibility, and amending an existing system via a scoped, versioned delta — to
  a bar a designer/engineer can build a consistent, accessible UI from. Composes
  with a design-system template tool + deep-research. Targets a textual markdown
  artifact, not rendered swatches. Not for reviewing a design system, not per-screen
  layout (wireframing), not a coded component library.
extensions:
  claude:
    when_to_use: "authoring or expanding a design-system document for a product, or amending an existing one via a versioned delta"
    argument-hint: "<the product direction / PRD (and any user-flows) to build a design system for; or the existing design system + a scoped change>"
version: "1.2.0"
forge:
  status: reviewed
  forged: 2026-06-04
  reviewed: 2026-06-13
---

# `authoring-design-system` — SKILL.md

> **Variant:** standard · **When to use:** producing (or amending) a design-system document from a product's direction, to a quality bar a designer/engineer can build a consistent, accessible UI from.

## Overview

This skill is the *how-to* of writing a usable, consistent, accessible design-system document — the reusable visual + interaction language a product's UI draws on (principles, design tokens, a component catalog, patterns, layout + internationalization conventions, accessibility standards, voice, and lifecycle/governance). It supplies the producer's **judgment**, not the section list. It assumes two collaborators: a **design-system template tool** that supplies the section *structure*, and a **deep-research capability** to ground tokens and components in established practice. The producer is handed the **product direction (and any user-flows)** and must **elaborate** it — never emit generic boilerplate. The bar to clear: a designer can build a consistent UI and an engineer can implement it from the document, the catalog covers every component the product's screens need, and the system is accessible. The document is the *vocabulary* later wireframes and hi-fi draw on — it precedes them.

The artifact is **textual markdown** — tokens as values + DTCG-shaped tables (hex/HSL/Oklch), type-scale + component spec tables. Not a rendered Figma file, not a compiled token package. The method is medium-independent; the artifact today is text.

## When to activate

- Authoring a new design-system document from a product's direction / PRD.
- Expanding a thin token set or component list into a full design system (foundations + catalog + patterns + accessibility + voice + governance).
- **Amending an existing design system** for a change (a new/changed token or component) — as a scoped, versioned delta (see Step 7).
- Filling a design-system template with researched, decision-complete content.

**Do NOT activate when:**

- Reviewing or grading a finished design system → use `reviewing-design-system` (it asserts the same bar this skill produces to).
- Defining per-screen layout / where components are placed → that is `authoring-wireframes`, which *references* the design system this skill produces.
- Producing the high-fidelity coded prototype → that is `authoring-hi-fi`, a downstream consumer.
- Shipping a coded component library (CSS/React) → this is the *document* (tokens + specs + rules), not the implementation.
- Authoring a different document type → use that type's skill.

## Inputs

Read **every document the plan hands you** — your `depends_on` set (the upstream documents discovery determined inform this one) — and trace this document's content back to them. The **recommended input set** that yields a production-grade design system: the **product-direction / PRD** (personas, purpose, surface area) and, where available, the **user-flows** (they signal which screens — and therefore which components — exist). On an **amend**, you are also handed the **existing design-system document** + the scoped change. This recommended set is **guidance, not a hard precondition** — be **self-contained**: produce from *whatever* context you actually receive; when an expected informing document is absent, proceed on what you have and surface the gap as an explicit assumption, never fabricate. **Use a research capability where one is available** (deep-research) to make the document comprehensive, not merely to fill the template.

## Workflow

### Step 1: Take the structure from the template tool — don't invent an outline

Get the section structure from your design-system template tool (comprehensive variant). Do **not** restate or re-derive a section list here; this skill supplies the method that *fills* those sections well. If no template is available, obtain a comprehensive structure (request/forge one, or fall back to the canonical set: principles → tokens → component catalog → patterns → layout & i18n conventions → accessibility → voice → lifecycle/governance), then proceed.

### Step 2: Load the product direction + surface area; identify the archetype

Read the product direction / PRD and any **user-flows**. **Identify the product archetype** (thin CLI/utility vs. content app vs. full interactive UI product) — it sizes the whole system, including which optional angles apply (i18n, multi-brand, governance). Where brand/visual direction is thin, make choices **explicit** (a stated Assumption or Open Question), never silently generic. **Audience is an owner decision** — record the target user + domain-literacy as a Decision; surface an assumed audience as an Open Question, never bake it in silently.

### Step 3: Research to ground tokens, components, accessibility, and conventions

Use a deep-research pass to ground tokens, the component set, patterns, the accessibility target, the token *format*, and the i18n/governance conventions in **established practice** rather than invent them. **If no research capability is available, do NOT fabricate** — state the chosen conventions as explicitly-flagged assumptions against the canonical defaults.

### Step 4: Apply the per-section method

Fill the template's sections to this method (depth for each lives in `references/`):

- **Principles** — 3–6 **opinionated, actionable** beliefs a reviewer could settle a disagreement with, each naming its tradeoff. Not platitudes.
- **Design tokens** — name every design decision as a token in **three tiers**: *primitive/reference* (raw value) → *semantic/system* (named by **intent**, references a primitive) → *component* (references a semantic). Name by **intent, not appearance** (`color.action.primary`, not `color.blue.500`) — the semantic layer is what components reference and what makes the system consistent + themeable. **Express tokens in the W3C DTCG format** (typed `$value`, aliasing) — this is **required at any size**, not just large systems (`references/tokens-dtcg.md`). Cover:
  - **Color** — primitive ramps + semantic role tokens (text / action / feedback / surface / border / focus); a recorded contrast ratio for every text + UI pairing (ties to accessibility). Use **modern color spaces** (Oklch / Display-P3 with sRGB fallback) where the product benefits; sRGB is a fine default.
  - **Typography** — a role × size **type scale** (display / headline / title / body / label) as a size / line-height / weight table, on a stated ratio; body line-height ≈ 1.4–1.6.
  - **Spacing & density** — one base unit on a 4/8px grid + a multiplicative scale; state a **density** stance for data-dense surfaces.
  - **Elevation** — a small named level set (resting → raised → overlay), each a shadow/surface, role-mapped.
  - **Motion** — duration + easing tokens composed into named transitions; include a **reduced-motion** stance.
  - **Iconography** — a stated icon grid/keylines, stroke weight, size set, and one style; document the rules even when assets are external.
  - **Theming** — light/dark and (where the product needs it) **multi-brand** are implemented by **re-pointing the semantic aliases** at per-theme/brand primitives over one fixed semantic/component tier — never forked components.
- **Component catalog** — see Step 5 for sizing; spec **each** component with the same six parts: purpose, **anatomy** (parts + the tokens each uses), **states** (default/hover/active/focus/disabled/loading/error as applicable), **variants** (type + size), **usage do/don't**, **accessibility** (role, keyboard, focus, contrast, state conveyance). Keep **one API vocabulary** across the catalog (the same variation axis named the same everywhere — `variant`/`size`/`state`, not `type` here and `mode` there; shared values compose dimensionally).
- **Patterns** — name the recurring multi-component scenarios the flows need (form validation, empty state, destructive-confirm, …), the components/tokens each composes, and the rules.
- **Layout & internationalization conventions** — breakpoints + grid (columns/gutter/margins) + min hit-target + focus order; and **internationalization/RTL** where the product is/will be localized: text-expansion headroom (flexible containers), logical CSS properties, RTL/bidi mirroring, locale font stacks, locale formatting. A stated single-locale tool may scope i18n out **explicitly**.
- **Accessibility standards** — numeric + checkable, to **WCAG 2.2 AA** (see Step 6).
- **Voice & content** — voice + a **tone spectrum** (formal↔playful) with the high-stakes rule (clarity over brand voice in errors/destructive moments); terminology (one term per concept); component copy rules (button = verb-first; **error = cause + fix**; **empty = guide-to-action**).
- **Lifecycle & governance** — **omittable** for a single-maintainer + single-consumer + non-versioned-external system; **required** above that threshold, and then document: versioning (semver) + changelog, deprecation + migration policy, contribution model, ownership, adoption/getting-started, and the recorded audience (`references/governance.md`).

### Step 5: Size the component catalog — the hard floor plus the standard set

The catalog must cover **both**: **(a) the surface-area hard floor** — every component the product's flows/screens actually use, each specced in full (non-negotiable); and **(b) the common standard set** sized to the archetype (a thin tool: a handful; a full UI product: the broad set). Where a needed component can't be fully specced from the available direction, surface it as an Open Question — don't invent its behavior.

### Step 6: Make accessibility numeric (WCAG 2.2 AA)

State **WCAG 2.2 AA** as the target and every threshold as a number (`references/accessibility-wcag22.md`): text contrast ≥ **4.5:1** (large/UI ≥ **3:1**); a **visible** focus indicator (SC 2.4.7, AA) that is **not obscured** when focused (SC 2.4.11, AA), and — adopting the stricter **AAA Focus Appearance** (SC 2.4.13) as a house rule — ≥ **2px** + **3:1** vs unfocused + adjacent; target size **24×24** (+ spacing exception); full keyboard operability; reduced-motion; no color-only meaning; per-component role/name/state conveyance. Bake a11y **into** the token specs (contrast, focus) and every component's accessibility part — not a later pass.

### Step 7: Amend mode — edit an existing system as a versioned delta

When handed an existing design system + a scoped change, **amend, don't regenerate** (`references/amend.md`). Scope the change to the token(s)/component(s) it touches **and its ripple** (every component referencing a changed token; every consumer of a renamed component; every theme alias affected). Make the **minimal in-place edit** — untouched tokens/components stay byte-for-byte. **Version the delta**: bump the system's semver (MAJOR breaking — rename/remove/retype; MINOR additive; PATCH fix) + a Keep-a-Changelog entry (Added/Changed/Deprecated/Removed/Fixed). For a breaking change, **deprecate-then-migrate** (deprecate in a minor → migration note → remove in a major), never silent removal. The alias layer is your friend — re-point a semantic alias rather than editing every component to shrink the blast radius.

### Step 8: Self-check against the bar before handing off

Confirm all hold (the same bar `reviewing-design-system` asserts): principles stated; tokens defined + DTCG + intent-named + components reference semantic tokens (never raw values); foundations cover grid/density/iconography/modern-color where the archetype needs them; every component fully specced (six parts) + one API vocabulary; catalog covers the hard floor + the archetype standard set; patterns present; layout + i18n addressed (or i18n explicitly scoped out); accessibility numeric to WCAG 2.2 AA; voice + copy rules present; lifecycle/governance present (or legitimately omitted below the threshold); grounded-not-boilerplate; on an amend, the delta is scoped + versioned + deprecation-safe. **Thin-direction gate:** if the surface area can't be inferred even approximately, surface a **blocker**, don't invent a catalog.

## Rules

**Hard rules (never violate):**

- **Compose, don't duplicate.** Take the section structure from the template tool; this skill supplies the method that fills it.
- **Name tokens by intent; express in DTCG.** Semantic tokens named for meaning (`color.feedback.danger`), components reference semantic tokens never raw values; tokens in the W3C DTCG format (typed + aliased) **at any size** — no values-table exception.
- **Theming is alias-swap.** Light/dark + multi-brand re-point semantic aliases over one fixed tier — never forked components.
- **Every component is fully specced + one API vocabulary.** Anatomy + states + variants + usage + accessibility, and the same variation axis named the same across the catalog.
- **Cover the surface-area floor.** Every component a real screen uses is in the catalog, fully specced.
- **Accessibility is numeric, to WCAG 2.2 AA.** Contrast; focus — visible + not-obscured (AA) plus the AAA Focus Appearance ≥2px/3:1 adopted as a house rule; target-size 24px; keyboard; reduced-motion; no color-only. "Accessible" without numbers is not a standard.
- **i18n: address or scope out explicitly.** For a localized product, cover text-expansion + logical properties + RTL; a single-locale tool states the scope-out — never silently omit.
- **Governance: omit below the threshold, require above it.** Single-maintainer + single-consumer + non-versioned-external may omit the lifecycle/governance section; otherwise it is required.
- **Amend = edit-not-redraw + versioned delta.** On a change, make the minimal scoped edit, version it (semver + changelog), deprecate-then-migrate breaking changes; never regenerate or revamp untouched parts.
- **Never fabricate.** Don't invent a palette, contrast figure, or convention to look grounded. Unknown → an explicitly-flagged assumption.
- **Textual medium.** Values + spec tables (markdown), not a rendered design file.
- **Buildable or not done.** Don't hand off a system a designer/engineer can't build a consistent, accessible UI from.

**Preferences (override-able):**

- "Comprehensive" sets *ambition*; stay **proportional** — completeness of decisions, not row count. A thin product collapses sections + trims the standard set + may scope out i18n/multi-brand and omit governance (the hard floor + DTCG + numeric a11y still hold).
- Keep principles to 3–6 crisp bullets; prefer conventional token tiers / type-scale roles.
- Prefer re-pointing a semantic alias over a breaking token change where it preserves compatibility.

## Gotchas

- **Value-named or non-DTCG tokens.** `color.blue.500` referenced by a button, or a flat hex list with no DTCG structure, kills theming + interoperability — name semantically, express in DTCG, even on a small system.
- **Half-specced components.** Variants but no states (or no accessibility) reads complete but can't be built consistently — all six parts, every component.
- **API drift.** `type` vs `variant` vs `mode` across components erodes the system — one vocabulary.
- **Catalog from the standard set only.** Skipping a component a real screen uses leaves a coverage hole — walk the flows first.
- **Aspirational accessibility.** No WCAG 2.2 target / no numbers = not a standard.
- **i18n as an afterthought.** Fixed-width text + physical CSS properties break translation — bake flexible containers + logical properties into foundations.
- **Regenerating on a change.** Rewriting the whole system for a one-token change (instead of a scoped versioned delta) is the amend anti-pattern — edit-not-redraw.
- **Generic fill.** Tokens/components true of any product = you elaborated the *template*, not the *product*.

## Anti-patterns

- **"I'll write the outline myself."** Duplicates the template tool — take the structure; supply method + bar.
- **"DTCG is only for big systems."** It's required at any size — a small system still gets typed/aliased tokens.
- **"Accessibility is a later pass."** Contrast, focus, keyboard live in the token + component specs — bake them in to WCAG 2.2.
- **"The standard set is the catalog."** It's half — the other half is every component the product's screens use.
- **"It's a small change, I'll regenerate the system."** Amend as a scoped versioned delta; never revamp untouched parts.
- **"The direction is thin, so I'll invent a full catalog."** Surface the missing surface area as a blocker/open-question.

## Output

A **design-system document** meeting the **Step 8 bar** (principles; DTCG intent-named tokens consistently applied; full foundations incl. iconography/grid/density/modern-color; every component fully specced + one API vocabulary; catalog covering the floor + standard set; patterns; layout + i18n; numeric WCAG 2.2 AA accessibility; voice + copy rules; lifecycle/governance where required; grounded-not-boilerplate; on an amend, a scoped versioned delta). The **abstract consumer** is downstream wireframing + hi-fi (which reference its components/tokens), UI engineering (which builds from it), and a reviewer (which asserts the same bar). Expressed textually (markdown); **precedes** wireframes/hi-fi one-directionally.

## Related

- A **design-system template tool** (content/template gateway) — supplies the section structure this skill fills.
- A **deep-research capability** — grounds tokens, components, patterns, the accessibility target, the DTCG format, and i18n/governance conventions.
- `reviewing-design-system` — asserts the same bar; author + reviewer share one bar so they don't drift.
- `authoring-wireframes` + `authoring-hi-fi` — **downstream** consumers: screens place this document's components and reference its tokens.
- The upstream **product-direction / PRD** (and optionally **user-flows**) — the input this skill elaborates; never a blank page.

## Progressive disclosure

- `references/tokens-dtcg.md` — the DTCG token format (tiers, typed `$value`, aliasing, theming/multi-brand, modern color spaces).
- `references/accessibility-wcag22.md` — the WCAG 2.2 AA numeric thresholds + per-component a11y.
- `references/i18n-rtl.md` — internationalization/RTL conventions (text-expansion, logical properties, locale typography).
- `references/governance.md` — lifecycle & governance policy (versioning, deprecation/migration, contribution, ownership, adoption, audience) + the omit-below-threshold rule.
- `references/amend.md` — amend mode (scope the ripple, edit-not-redraw, versioned delta, deprecate-then-migrate).
- `references/sources.md` — research provenance for the method + the token/component conventions + the accessibility thresholds.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap).
- Body ≤ ~500 lines / 5,000 tokens.
- Heavy content lives in `references/`, loaded on demand.
