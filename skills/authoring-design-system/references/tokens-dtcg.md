# Design tokens — the DTCG format, tiering, theming

Depth for the Design tokens method. The token architecture is the consistency + theming guarantee.

## Three tiers

1. **Primitive / reference** — raw values, no meaning: `color.blue.500 = #1A73E8`, `space.4 = 16px`.
2. **Semantic / system** — named by **intent**, aliases a primitive: `color.action.primary → {color.blue.500}`, `color.text.default`, `space.inset.md`. This tier is what components reference; it is what makes the system consistent + themeable.
3. **Component** — references a semantic: `button.background → {color.action.primary}`. Optional; use where a component needs its own indirection.

Components reference **semantic** (or component) tokens, never primitives or raw values. A raw value in a component spec is the #1 consistency failure.

## Naming by intent

Name semantic tokens for what they **mean**, never their value: `color.feedback.danger`, not `color.red.600`. A coherent hierarchical pattern (`category.role.variant.state`) keeps tokens discoverable. Intent naming is what lets a theme swap the underlying value without touching a component.

## The W3C DTCG format (required at any size)

Express tokens in the **Design Tokens Community Group** format (first stable version 2025.10): a JSON shape with typed values and aliasing.

- Each token: `$type` + `$value` (+ optional `$description`).
- Aliasing: curly-brace references (`{color.blue.500}`) or JSON-Pointer.
- Groups for structure.
- Reference implementations: Style Dictionary, Tokens Studio, Terrazzo; consumed by Figma, Penpot, Sketch, Framer, Supernova, zeroheight.

This is **required at any size** — even a small system expresses typed/aliased tokens (no flat-hex-list / values-table exception). The skill *documents* tokens (the source of truth) + may name the transform tool; it does not run the build pipeline. The artifact is the textual token doc (DTCG-shaped tables/JSON), not a compiled package.

Example (DTCG-shaped):

```json
{
  "color": {
    "blue": { "500": { "$type": "color", "$value": "#1A73E8" } },
    "action": { "primary": { "$type": "color", "$value": "{color.blue.500}" } }
  }
}
```

## Theming — light/dark + multi-brand

Theming re-points the **semantic aliases** at different primitives over **one fixed** semantic/component tier — never re-specifies components. Light/dark are two alias sets over one vocabulary. **Multi-brand** extends this: each brand is another alias set (its own primitives) over the same semantic + component tiers. The DTCG 2025.10 spec adds standardized theming support. A theme implemented by forking components is the anti-pattern.

## Modern color spaces (proportional)

CSS Color Module 4 + DTCG support **Oklch** (perceptual lightness → even ramps + predictable contrast steps) and **Display-P3** (wide gamut). Author ramps in Oklch for uniform steps; use P3 with an sRGB fallback where the product benefits. sRGB hex is a fine default for a utility product — unlike the DTCG *format* (universal), the color *space* is proportional.

## Proportionality

DTCG format is universal. Proportional only in **depth**: a utility product gets primitive + semantic tiers + light theme in DTCG; a multi-brand UI product gets the full tier + alias + multi-brand. Oklch/P3 and multi-brand are proportional to need.
