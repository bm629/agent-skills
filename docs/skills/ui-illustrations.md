# ui-illustrations

> Add illustration and imagery to a web app UI — empty states, onboarding, error
> pages, success moments — without tipping a data-dense product tool into
> decoration. Covers the placement doctrine (where imagery helps vs clutters,
> incl. the auth split-panel exception and the no-data-surfaces rule), sourcing
> from the established free libraries (unDraw / Storyset / LottieFiles) with the
> license traps mapped, recoloring sourced SVGs to design tokens so one asset
> follows light/dark themes, correct SVG-in-React/Vite integration (inline vs
> `<img>`, CLS + bundle discipline), animated imagery (Lottie) with
> reduced-motion accessibility, and empty-state craft (anatomy, the four
> variants, consistency).

**Skill file:** [`skills/ui-illustrations/SKILL.md`](../../skills/ui-illustrations/SKILL.md)
**Version:** 1.0.0

## Purpose

The typical product/ops tool shows bare text where imagery would carry warmth and
orientation — and when teams do add art, the failure modes are predictable: mixed
styles, license obligations silently violated, illustrations that glow wrong on dark
mode, decorative images announced to screen readers, layout shift, and art bolted onto
data surfaces where it's noise. This skill sources and integrates existing
illustration correctly end-to-end: pick the placement, pick the source, check + record
the license, hold one style family, recolor to tokens, embed without CLS/bundle
regressions, and wire accessibility — including animated imagery that respects
reduced motion. It does not teach drawing original art.

## When to activate

- ✅ A screen shows a bare "No items yet" and needs a real empty state.
- ✅ Adding onboarding/first-run, error-page (404/500/permission), or success-moment imagery.
- ✅ Choosing an illustration source, answering an attribution/licensing question, or matching sourced art to the app's palette and dark mode.
- ✅ Embedding an SVG or Lottie file in a React codebase and wiring its accessibility.

### When NOT to activate

- Icons (lucide, Heroicons) — a separate asset class with its own conventions.
- UI element/interaction motion — `motion-react` owns that; imagery *files* (incl. Lottie) are owned here.
- Drawing original illustration or authoring an illustration design language — designer/vendor work.
- Marketing-site hero/photography art direction.

## What it covers

- **Placement doctrine:** the helps-vs-clutters table — empty states / onboarding /
  errors / success yes; persistent data surfaces and form decoration no; loading
  moments are skeleton/spinner territory; the auth split-panel is the sanctioned
  exception. Proportionality for ops tools.
- **Sourcing + licensing:** unDraw (default: consistent style, color customization,
  no attribution, no-AI-training clause), Storyset (richer/animated scenes, free tier
  REQUIRES visible "Designed by Freepik" attribution — and the paid tier naming is
  inconsistent at the source, so confirm at adoption), LottieFiles (Lottie Simple
  License: commercial OK, share-alike modifications). The durable practice: license
  terms drift, so re-check the live page at adoption and record source + license +
  date next to the asset. What every source prohibits (pack redistribution).
- **Style consistency:** one family per product; the dimensions to hold constant.
- **Token recolor:** replacing hardcoded fills with semantic CSS variables so the same
  asset follows theme switches; what stays literal; `currentColor`'s monochrome limit.
- **SVG-in-React integration:** inline component (Vite `?react` via vite-plugin-svgr)
  vs `<img>` (`?url` + lazy) decision, per-path sizing rules that prevent layout
  shift, bundle discipline (inline small hot-path art only).
- **Dark mode:** the three strategies (token recolor / per-theme pairs — theme class
  for toggle apps, media query only for OS-driven theming / filter adaptation) and
  the audit-both-themes rule.
- **Animated imagery:** `lottie-react` embedding with an SSR-safe `useReducedMotion`
  hook AND an explicit pause/play effect (a runtime `autoplay` change alone does not
  stop a running animation); WCAG 2.2.2 stated precisely (auto-playing motion >5 s
  TOTAL — looping or not — needs a pause control); lazy-loading heavy JSON.
- **Empty-state craft:** the anatomy (art + headline + explanation + action), the
  four variants (first-run / cleared / no-results / error — never mislabel an error
  as emptiness), size discipline, app-wide consistency.
- **Accessibility contract:** decorative (`aria-hidden`/`alt=""` + strip the shipped
  `<title>`) vs informative (real alt text); flash limits; non-text contrast for
  meaning-carrying imagery in both themes.

## Structure

- `SKILL.md` — placement doctrine, sourcing decision path, integration quick path, a11y defaults, rules/gotchas/anti-patterns.
- `references/sourcing-and-licensing.md` — the landscape table, per-source license snapshots (dated), attribution mechanics, the record-the-license practice.
- `references/svg-integration-and-theming.md` — inline/img decision, Vite pipeline, CLS + bundle rules, token recolor, the three dark-mode strategies, Lottie embedding.
- `references/empty-states-and-a11y.md` — anatomy, the four variants, onboarding/error pages, the decorative-vs-informative contract, animated-imagery rules, microcopy notes.
- `references/sources.md` — research provenance (live license pages, dated snapshots).

## Provenance

Forged 2026-07-11 via the skill-forge pipeline against the live unDraw / LottieFiles /
Storyset license pages and the vite-plugin-svgr + lottie-react sources; verified across
5 fresh-reviewer cycles (cold subagents fact-checking live sources + adversarial
behavioral simulations — including one that caught the Storyset paid-tier naming
contradiction at the source itself, and one that verified lottie-react's runtime
autoplay behavior in the library source).
