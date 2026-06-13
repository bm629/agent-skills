# The buildability bar — conditions expanded (pass/gap signals + worked findings)

Depth for Step 2. Each condition with a sharper pass/gap signal and a worked finding. Load when a borderline call needs calibration. The conditions are the (reviewing+both) angles single-sourced with `authoring-design-system`.

## 1. Principles stated
- Pass: 3–6 opinionated, actionable principles, each naming a tradeoff. Gap: absent, or platitudes ("be delightful").

## 2. Tokens — defined, DTCG, intent-named, consistent
- Pass: color (incl. semantic roles), type, spacing, elevation, motion as named tokens with values, in DTCG (typed `$value` + aliasing) at any size; components reference semantic tokens.
- Gap: a token family missing/valueless; a flat hex list with no DTCG structure; a component spec with a raw value (`#1A73E8`, `16px`) or a value-named token.
- Collapse: none for DTCG; Oklch/P3 proportional (sRGB-only is fine).
- Finding: *revise — Tokens (cond.2): tokens are a flat hex table with no `$type`/aliasing. Fix: express in DTCG (typed values + curly-brace aliases); the "Card" spec's `#FFF` should reference `color.surface.default`.*

## 3. Foundations breadth
- Pass: grid/layout + density + iconography present where the archetype uses them. Gap: a UI product with no grid or no icon foundation it clearly needs. Collapse: a thin tool with no icons/complex layout omits them.

## 4. Theming via alias-swap
- Pass: light/dark + multi-brand re-point semantic aliases over one fixed tier. Gap: a theme implemented by forking components. Collapse: single-brand single-theme.

## 5. Component completeness (five parts)
- Pass: anatomy + states + variants + usage do/don't + accessibility, per component. Gap: any one missing (variants but no states; no a11y line).
- Finding: *revise — Component completeness (cond.5), "Modal": no states + no accessibility. Fix: add states (open/closing, focus-trapped) + a11y (role=dialog, focus trap+restore, Esc, labelled by title).*

## 6. Component API consistency
- Pass: one property/option/default vocabulary across the catalog; shared values compose. Gap: `type` vs `variant` vs `mode` for the same axis across components. Collapse: a tiny catalog trivially holds.

## 7. Catalog coverage — both floors
- Pass: every component a real screen uses (hard floor, fully specced) + the archetype-sized standard set. Gap: a screen needs a component the catalog omits/under-specs. Collapse: the standard set scales with archetype (no maximalism). The hard floor never collapses.

## 8. Patterns present
- Pass: the recurring multi-component scenarios the flows need. Gap: a needed pattern absent.

## 9. Layout + internationalization
- Pass: breakpoints/grid/focus-order; for a localized product, i18n/RTL (text-expansion, logical properties, RTL/bidi, locale fonts). Gap: a localized product ignoring i18n; a reflowing screen silent on reflow. Collapse: a stated single-locale tool scopes i18n out **explicitly** (silent omission is still a gap).

## 10. Accessibility numeric, WCAG 2.2 AA
- Pass: WCAG 2.2 AA target + thresholds — text ≥4.5:1 (large/UI ≥3:1); visible + not-obscured focus (SC 2.4.7/2.4.11, AA) plus the AAA Focus Appearance ≥2px/3:1 (SC 2.4.13) as a house rule; target size 24×24 (+ spacing exception); keyboard; reduced-motion; no color-only; per-component role/name/state.
- Gap: aspirational/non-numeric a11y, or missing not-obscured (AA), the Focus-Appearance ≥2px/3:1 house rule, or target-size. Collapse: none — a11y is non-negotiable.

## 11. Voice/content
- Pass: voice + tone spectrum (clarity over brand voice in high-stakes), terminology (one term per concept), copy rules (button verb-first; error = cause+fix; empty = guide-to-action). Gap: absent for a copy-bearing product; error/empty rules without cause+fix / guide-to-action. Collapse: no user-facing copy → light.

## 12. Lifecycle & governance (above threshold)
- Pass (above threshold): versioning + changelog, deprecation/migration, contribution, ownership, adoption, audience-as-recorded-decision. Gap (above threshold): governance/versioning absent, or an assumed audience drives the vocabulary.
- Collapse: **fully omittable** below the threshold = single-maintainer + single-consumer + non-versioned-external. Manufacturing a governance gap there is a false-revise.

## 13. Grounded + usable downstream
- Pass: tokens/components reflect this product; gaps as assumptions/open-questions; wireframing/hi-fi/engineering can build without asking. Gap: generic fill; a fabricated brand/contrast answer; a dangling reference.

## Delta-review (Step 2b) — when judging an amend

- **Scope-confinement** — only the stated tokens/components changed; no unrelated rename/palette-churn/re-tiering. Out-of-scope ⇒ revise/split.
- **Ripple/regression** — no component left referencing a removed/renamed token; alias layer resolves; themes still cohere (no silent dark-mode/brand break).
- **Versioning** — semver bump matches the change class (rename/remove/retype ⇒ MAJOR; additive ⇒ MINOR; fix ⇒ PATCH); changelog matches the diff.
- **Deprecation-safe** — a breaking change carries deprecation + migration; no silent removal.
- **Coherence + re-review proportionality** — fits the existing tiering/API; judge the delta, don't re-litigate untouched parts.
- Finding: *revise — Delta (Step 2b): `color.action.primary` renamed but the "Button"/"Link" specs still reference the old name (orphaned), and the bump is MINOR. Fix: bump MAJOR, update the dependents (or deprecate-then-migrate the old alias), add the changelog entry.*
