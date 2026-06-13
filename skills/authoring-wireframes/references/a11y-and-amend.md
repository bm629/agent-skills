# Screen-composition a11y + amend — depth reference

> Depth for `authoring-wireframes` Step 5 (Accessibility) + Step 8 (Amend). Load for an a11y pass or an amend. Portable; provenance in `sources.md`.

## The a11y boundary — component-contract vs screen-composition

The design/UX pair set is non-overlapping. Two halves of accessibility:

- **Component-contract a11y — the DESIGN-SYSTEM owns it.** Each component is accessible in its own right: its **contrast** (4.5:1 text / 3:1 large+UI), its **focus appearance** (WCAG 2.2 SC 2.4.13), its own **target-size**, its **keyboard** behavior, its **role/name/state**. The wireframe never re-judges these pixel/component values.
- **Screen-composition a11y — the WIREFRAME owns it.** How *this screen composes* those components. This is what the wireframe annotates (below).

**Standalone fallthrough:** if a product has neither a design-system nor a downstream hi-fi pass, component-contract a11y (contrast/focus-appearance) is judged by nobody — record it as an explicit **assumption/deferral** ("contrast + component a11y deferred — no DS/hi-fi gate present"), never silently drop it.

## Screen-composition a11y the wireframe owns (WCAG 2.2)

- **Landmarks / regions** (SC 1.3.1) — each layout region maps to a landmark (banner/header, nav, main, complementary/sidebar, contentinfo/footer) so AT users navigate by region.
- **Heading hierarchy** (SC 1.3.1) — **one h1 per screen**, no skipped levels; the heading outline matches the visual hierarchy.
- **Reading / focus order** (SC 2.4.3) — a meaning-preserving order; source/DOM order matches intended reading order, incl. when conditional content is revealed (disclosure/modal — focus moves predictably).
- **Accessible names** (SC 4.1.2) — every control, **especially icon-only buttons**, has an annotated accessible name where the visible affordance lacks text.
- **Keyboard operability** — every affordance reachable + operable by keyboard; **no mouse-only/gesture-only** required step; annotate custom-widget keyboard behavior.
- **Target-size reservation** (SC 2.5.8, AA) — reserve a **≥24×24 CSS-px** hit area at structure time; touch tiers reserve larger. A *reservation*, not a pixel-contrast judgment.
- **Focus-not-obscured** (SC 2.4.11, AA) — a sticky header/footer or non-modal overlay must not cover the focused element; reserve scroll-padding / sticky-region height (a layout decision).
- **Non-color-only intent** (SC 1.4.1) — state/meaning never by color alone; pair color with an icon/text/shape (the wireframe reserves the non-color signal; the DS sets the color).

Non-negotiable baseline (applies at any screen size): landmarks + one h1 + accessible names + keyboard-operable. Sticky/target-density/focus-order specifics apply only where the screen has them.

## Amend — edit, don't redraw

Amending a wireframes doc is a **scoped, reviewed, versioned diff** against the existing document, never a regenerate. Scope unit = a **screen / state / region**.

### WA1 — Scope + ripple analysis
Identify the touched screen(s)/state(s)/region(s), then trace the ripple:
- every screen reusing a **changed shared region** (app-shell / nav / header/footer);
- every **screen-inventory row** / flow hand-off / screens-index entry referencing an edited/removed screen;
- every screen naming a **DS component that changed or was deprecated**;
- every screen added/removed by an upstream **flow** change.

### WA2 — Surgical amendment
- Minimal in-place edit; **untouched screens + their sketches/annotations/inventory rows stay byte-for-byte unchanged**; no gratuitous re-drawing/re-numbering.
- The one legitimate wide ripple: a **shared-region change applied to ALL reusing screens in one pass** (not screen-by-screen drift).
- Preserve stable screen + component names; keep each sketch ⇄ its annotations in sync.

### WA3 — Versioning & changelog (the doc's OWN version)
- **MAJOR** — a removed/renamed screen or a removed per-screen state (breaks the downstream build/hi-fi contract).
- **MINOR** — an added screen/state/region/component.
- **PATCH** — an annotation/notation/copy-intent fix.
- Add a **Keep-a-Changelog** entry (Added/Changed/Deprecated/Removed/Fixed) at the screen/state grain. (Distinct from the skill's own semver.)

### WA4 — Deprecation & removal
- Mark a screen/state **deprecated** in a MINOR (note the replacement) before **removing** it in a MAJOR.
- On removal, confirm no inventory row / flow hand-off / screens-index entry still references it, and prune the inventory.
- A removed shared region / nav entry is **announced**, not silently dropped.
