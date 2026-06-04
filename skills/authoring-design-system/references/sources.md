# Sources — `authoring-design-system`

Research provenance for the method + quality bar in `SKILL.md`. Synthesized 2026-06-04 from a deep-research pass; external content passed through a content sanitizer (clean — descriptive design-system terminology, no embedded commands/URLs) before synthesis. All claims paraphrased. ≥2 independent sources per claim.

## Primary research

A consolidated design-system-authorship research pass corroborated the per-section method, the token/component conventions, and the usability/consistency/accessibility quality bar across reputable design-system references:

- **Material Design 3** (m3.material.io) — design tokens; the role × size type scale (display / headline / title / body / label); spacing/grid; elevation levels; motion (duration + easing).
- **W3C Design Tokens Community Group — Format Module 2025.10** (designtokens.org, w3.org/community/design-tokens) — the vendor-neutral token format and types (color, dimension, fontFamily, fontWeight, duration, cubicBezier, and composite shadow/typography).
- **IBM Carbon Design System** (carbondesignsystem.com) — per-component documentation structure (usage / code / accessibility), states + variants, accessibility as shared responsibility.
- **Shopify Polaris** — component documentation plus voice/content guidelines folded into the design system.
- **W3C WCAG 2.2** (w3.org/TR/WCAG22) + **WebAIM** (contrast) — conformance targets and thresholds.
- **EightShapes / Nathan Curtis** — "Naming Tokens in Design Systems" (intent-based naming; category.property.variant taxonomy).
- Design-system documentation structure guides — Contentful, Netguru, UXPin, Magic Patterns, Prototypr.

## Corroborated claims (used in the body)

- **Canonical section set** (principles, design tokens, component catalog, patterns, accessibility standards, voice) — multiple sources; the structure itself is owned by the template tool, not this skill.
- **Three-tier tokens + intent naming** (primitive/reference → semantic/system → component; name by intent not appearance) — EightShapes/Curtis, Contentful, Material 3.
- **Type scale roles** (display / headline / title / body / label, each in sizes) as a textual size/line-height/weight table — Material 3.
- **Spacing on a 4px/8px grid; named elevation levels; motion via duration + easing tokens** — Material 3, W3C DTCG.
- **Per-component six-part spec** (anatomy, states, variants, usage do/don't, accessibility) — Carbon, Polaris, Magic Patterns, UXPin.
- **Accessibility thresholds** — WCAG 2.2 AA: text contrast ≥4.5:1 (large ≥3:1), non-text/UI contrast ≥3:1, visible focus ≥3:1 (2.4.11 Focus Appearance), full keyboard operability, no color-only information, reduced-motion — W3C WCAG 2.2, WebAIM.
- **Voice/content folded into the design system** — Polaris is the canonical example.
- **Catalog sizing** (the product's actually-used components as a hard floor + the standard set, archetype-keyed) — synthesized from the component-documentation guidance across sources.

## Note

The same research underpins the companion `reviewing-design-system` skill (the shared dossier), so the author's quality bar and the reviewer's quality bar stay single-sourced and aligned.
