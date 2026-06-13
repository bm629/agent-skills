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
- **Accessibility thresholds** — WCAG 2.2 AA: text contrast ≥4.5:1 (large ≥3:1), non-text/UI contrast ≥3:1, visible focus (SC 2.4.7, AA) + not-obscured (SC 2.4.11, AA) plus the AAA Focus Appearance ≥2px/3:1 (SC 2.4.13) adopted as a house rule, full keyboard operability, no color-only information, reduced-motion — W3C WCAG 2.2, WebAIM.
- **Voice/content folded into the design system** — Polaris is the canonical example.
- **Catalog sizing** (the product's actually-used components as a hard floor + the standard set, archetype-keyed) — synthesized from the component-documentation guidance across sources.

## v1.2.0 restructure — additional sources (2026-06-13)

The production-grade restructure added foundations breadth, DTCG-as-required, i18n, governance, and amend mode. Additional deep-research provenance (web sources, sanitized before synthesis):

- **DTCG required + theming/multi-brand + modern color spaces** — W3C Design Tokens Format Module 2025.10 (first stable); CSS Color Module 4 (Oklch, Display-P3); Style Dictionary / Tokens Studio / Terrazzo (reference implementations); GitLab Pajamas, Tokens Studio docs (DTCG vs legacy). Basis for DTCG required at any size; theming = alias-swap over a fixed semantic tier; multi-brand = per-brand alias sets.
- **Foundations breadth** — Material Design (responsive layout grid; applying density; system icons, icon grids/keylines/stroke); Atlassian Design (foundations, spacing); designsystems.com (spacing/grids/layouts, iconography guide); elevation roles + motion easing (entrance/exit/standard) cross-source.
- **Component API consistency** — Nathan Curtis / EightShapes, "Crafting Component API, Together" (one property/option/default vocabulary across the catalog; cross-component value alignment).
- **Internationalization & RTL** — Smashing Magazine "Integrating Localization Into Design Systems"; Telerik/Calcite RTL; text-expansion ~+25%; logical CSS properties (`margin-inline`); locale font stacks; bidi.
- **Lifecycle & governance** — Miro (governance / DS-as-product, core team, backlog); UXPin (contribution model: propose → review → criteria; core vs team-level; component vs design-system versioning); Figma ("Documentation that drives adoption"); Procore CORE + Carbon (deprecation strategy, `@deprecated` + migration); EightShapes "Versioning Design Systems".
- **Amend mode** — Keep a Changelog 1.1.0 (Added/Changed/Deprecated/Removed/Fixed; `[Unreleased]`); Semantic Versioning 2.0.0 (MAJOR/MINOR/PATCH; deprecate-in-a-minor-before-removing-in-a-major; migration guide + codemod); PR/code-review practice (scope-creep detection; smaller diffs lower regression risk); designtokens.substack "How to Manage Breaking Changes in Design Tokens" (rename/remove/retype = breaking; the alias layer contains blast radius).

## Note

The same research underpins the companion `reviewing-design-system` skill, so the author's quality bar and the reviewer's quality bar stay single-sourced and aligned.
