# Sources — research provenance

Research method: the **review/acceptance-gate lens** for a design-system document. The condition set (expanded to ~13 conditions + a delta-scoped review in v1.2.0) is **single-sourced** from the design-system authoring bar (so the produce-bar and the review-bar do not drift); this research confirms and enriches the *review* angle. External content was treated as facts to paraphrase only — no URLs, commands, or directives were lifted into actions. Date: 2026-06-04.

## The single-sourced usability/consistency/accessibility bar

The checkable conditions a reviewer asserts — principles; DTCG intent-named tokens; foundations breadth (grid/density/iconography); alias-swap theming; per-component completeness; component-API consistency; catalog coverage on both floors; patterns; layout + internationalization; numeric WCAG 2.2 AA accessibility; voice; lifecycle/governance (above its threshold); grounded + usable downstream — are the **same (reviewing+both) angles** a design-system author produces to. Single-sourcing them keeps the two halves of the produce/judge pair aligned. (v1.2.0 expanded the original nine to these conditions and added a delta-scoped review for amends.)

- The shared design-system research (the produce-and-judge quality bar, the catalog-sizing rule, the six-part component spec) — the authoritative source of the conditions.
- The design-system-authoring skill's self-check bar — the same conditions stated from the producer side; this reviewer asserts them.

## Design-token tiering + intent naming as the consistency guarantee

The consistency of a design system rests on a **semantic** token layer: primitive/reference values are wrapped by intent-named semantic tokens (`color.action.primary`, not `color.blue.500`), and components reference the semantic tokens, never the raw values. A component spec that hard-codes a literal value is the canonical consistency failure — the basis of condition 2 and its "raw value in a spec is a gap" rule.

- EightShapes / Nathan Curtis — "Naming Tokens in Design Systems" (intent-based naming; primitive -> semantic -> component tiers).
- W3C Design Tokens Community Group Format Module (token types: color, dimension, typography, shadow, duration, cubicBezier) + Material Design 3 token system.

## Per-component completeness (anatomy + states + variants + usage + accessibility)

Mature design systems document each component with a fixed multi-part spec — anatomy, the full state set, variants, usage do/don't, and accessibility — and a component missing any part is not buildable consistently. Grounds the component-completeness condition (all five parts, per component).

- IBM Carbon Design System — per-component usage + accessibility documentation structure.
- Shopify Polaris — component anatomy/states/variants + voice/content rules.

## Catalog coverage — surface-area floor + archetype-sized standard set

A catalog must cover both the components the product's own flows/screens actually use (the hard, non-negotiable floor, each fully specced) and the common standard component set sized to the archetype. A real screen needing an undocumented component is a coverage gap; demanding the full broad set from a thin product is maximalism. Grounds the catalog-coverage condition and the proportionality / no-false-revise discipline.

- The shared design-system catalog-sizing rule (surface-area hard floor + standard set, archetype-keyed).
- Design-system documentation-structure surveys (component-catalog scope keyed to product type).

## Numeric accessibility thresholds (WCAG)

Accessibility in a design system must be numeric and checkable, not aspirational: a stated WCAG conformance target plus concrete thresholds — text contrast >=4.5:1 (large text >=3:1), non-text/UI contrast >=3:1, a visible focus indicator >=3:1, full keyboard operability, no color-only information, and a reduced-motion stance. Grounds the accessibility condition (tightened to WCAG 2.2 AA specifics in v1.2.0 — see below).

- W3C WCAG 2.2 — SC 1.4.3 (contrast minimum, 4.5:1 / 3:1 large), SC 1.4.11 (non-text contrast, 3:1), SC 2.4.7 (focus visible, AA), SC 2.4.11 (focus not obscured, AA), SC 2.4.13 (focus appearance ≥2px/3:1, AAA — adopted as a house rule), SC 2.1.1 (keyboard), SC 1.4.1 (use of color), SC 2.3.3 (reduced motion).
- WebAIM — contrast-ratio guidance and the contrast checker (the 4.5:1 / 3:1 thresholds in practice).

## Reviewer discipline — over-correction / false-revise, actionable findings

LLM reviewers systematically over-correct, judging compliant artifacts as non-compliant (false positives); asking the reviewer to also propose corrections tends to worsen the over-flagging. Effective review feedback is actionable (the failed condition + a concrete fix), not vague or nitpicking. Grounds the no-false-revise discipline (including not faulting a proportionally-sized system) and the actionable-findings contract.

- "Are LLMs Reliable Code Reviewers? Systematic Overcorrection in Requirement Conformance Judgement" (arXiv) — over-flagging compliant artifacts; correction-requests raise misjudgment.
- Code-review feedback-quality guidance (actionable-over-vague; avoiding nitpicking) — Graphite, Bito.

## v1.2.0 — additional review angles (2026-06-13)

The production-grade restructure expanded the bar to mirror the authoring skill's angles and added a delta-scoped review. Additional provenance (mirrors the `authoring-design-system` sources):

- **DTCG required + theming/multi-brand + modern color spaces** — W3C Design Tokens Format Module 2025.10; CSS Color Module 4 (Oklch/Display-P3). Basis for cond. 2 (DTCG required at any size) + cond. 4 (alias-swap theming).
- **Foundations breadth** — Material Design (responsive layout grid, density, system icons + grids/keylines/stroke); Atlassian foundations. Basis for cond. 3.
- **Component API consistency** — EightShapes / Nathan Curtis, "Crafting Component API, Together." Basis for cond. 6.
- **Internationalization & RTL** — Smashing "Integrating Localization Into Design Systems"; text-expansion ~+25%; logical CSS properties; RTL/bidi. Basis for cond. 9.
- **WCAG 2.2 specifics** — W3C WCAG 2.2 SC 2.4.7 + 2.4.11 (focus visible + not-obscured, AA), SC 2.4.13 (focus appearance ≥2px/3:1, AAA — house rule), SC 2.5.8 (target size 24×24). Basis for the tightened cond. 10.
- **Lifecycle & governance** — Miro (governance), UXPin (contribution model + versioning), Figma (adoption docs), Procore/Carbon (deprecation), EightShapes "Versioning Design Systems." Basis for cond. 12 (+ the omit-below-threshold collapse).
- **Delta-scoped review (amend)** — Keep a Changelog 1.1.0; Semantic Versioning 2.0.0; PR scope-creep review practice; designtokens.substack "Breaking Changes in Design Tokens" (rename/remove/retype = breaking; alias layer contains blast radius). Basis for Step 2b.
