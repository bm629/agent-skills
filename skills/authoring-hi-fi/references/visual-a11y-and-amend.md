# Visual polish + numeric a11y + amend (depth)

Loaded on demand by `authoring-hi-fi`. Depth on the polish bar (objective + the five named heuristics), the numeric WCAG 2.2 AA judgment on the render, and the amend token-ripple procedure.

## Visual execution depth

Realize the wireframe's structure + the DS tokens to pixels:

- **Color** — token-backed; semantic roles (primary/muted/destructive/…), not arbitrary hues; sufficient contrast (see a11y below).
- **Typography** — a real type scale (e.g. a modular scale), weight contrast for hierarchy, line-height for readability (~1.4–1.6 body), a comfortable measure (~45–75 chars).
- **Spacing** — the 8pt cadence realized (4pt for dense surfaces); consistent gaps; no off-cadence one-offs.
- **Elevation / radius / icons / imagery** — DS elevation tokens, consistent radius, a real icon set, placeholder-safe local/inline imagery (no arbitrary external fetches).
- **Realized hierarchy** — the wireframe's structural priority expressed in real contrast/scale/weight/color/position; the primary action visually dominant; scanning patterns (F/Z) respected; related items grouped (Gestalt).

## The polish bar: objective subset + five named aesthetic heuristics

### Objective subset (checkable)
Grid alignment · consistent spacing scale (no off-cadence gaps) · optical balance · no clipped/overlapping/orphaned elements · on-token values · consistent treatment across sibling screens.

### The five named aesthetic heuristics (judged, but each named + articulable)
The program judges these (visual polish IS the hi-fi deliverable), but a `revise` must **name which heuristic fails and why** against the render — a pure out-of-set personal preference (a specific hue, "a different layout would look nicer") is NOT a gap.

1. **Balance / visual-weight distribution** — weight is distributed, not lopsided; no one corner overloaded while another is empty. *Looks-like:* the composition feels stable; large/dark/dense elements are counter-weighted.
2. **Whitespace & restraint** — intentional negative space; not cramped, not a wall; not over-decorated (no gratuitous borders/shadows/colors). *Looks-like:* content can breathe; every element earns its place.
3. **Spacing rhythm** — a consistent, repeating spacing cadence (the 8pt rhythm felt, not just present); related groups share one gap, unrelated groups a larger one. *Looks-like:* the eye reads predictable intervals, not random gaps.
4. **Focal clarity** — one clear primary emphasis per screen; the eye knows where to land first. *Looks-like:* the primary action/headline wins the contrast/scale contest; secondary content recedes.
5. **Aesthetic cohesion** — a "designed", intentional feel — one consistent visual voice across components, not assembled-from-parts. *Looks-like:* the screens look like one product, not a parts bin.

## Numeric WCAG 2.2 AA — on the render (the locked SC set)

Because the artifact is real pixels, pixel-WCAG is JUDGED here (the wireframe only reserved it). Bake it in and self-check on the render:

- **1.4.3 Contrast (Minimum)** — AA — text ≥ **4.5:1** (large text ≥18.66px bold / ≥24px → 3:1).
- **1.4.11 Non-text Contrast** — AA — **3:1** for UI component boundaries, icons, focus rings, graphical objects.
- **2.4.7 Focus Visible** — AA — a visible keyboard-focus indicator on every interactive element.
- **2.4.11 Focus Not Obscured (Minimum)** — AA — the focused element isn't hidden by sticky/overlay chrome.
- **2.5.8 Target Size (Minimum)** — AA — interactive targets ≥ **24×24 CSS px** (with the spacing/inline exceptions); primary touch targets larger.
- **2.4.13 Focus Appearance** — **AAA**, adopted as a program **house rule** — focus indicator ≥2px perimeter + ≥3:1 against adjacent colors.
- Plus: keyboard operability + logical focus order (real in the DOM, carried from the wireframe); `prefers-reduced-motion` honored; semantic landmarks, heading order, accessible names real in the markup.

**Tooling:** run **axe-core on the rendered HTML** (catches contrast, names, roles, landmarks) + the **vision review** for what axe can't see (focus *appearance*, contrast over imagery, meaningful visual order) + a manual/AT spot-check. **Never disable a rule to pass** — fix the failure in the **token map** (a contrast miss → adjust/add a token); a suppressed rule is itself a finding.

## Amend — token-ripple procedure (edit + re-render the delta)

The distinctive hi-fi ripple is a **DS token change**: because every screen consumes the tokens through one map, a token-value change re-renders every consumer.

1. **Scope + ripple** — list the touched screen(s) AND the ripple set: every screen consuming a changed token (via the map), every screen reusing a changed shared layout/component, every screen added/removed by an upstream wireframe change, every screen naming a changed/deprecated DS component.
2. **Apply once, re-render the delta** — change the token **once in the map** (`:root`/`@theme`), then re-render + re-vision-review **all consumers** in one pass; for a per-screen edit, touch only that screen. Untouched screens' **code** stays byte-stable + their **screenshots are not re-captured** (not byte-diffed). Never hand-edit a token's value per screen (the #1 amend regression).
3. **Version + changelog** — bump the doc's own version: MAJOR (removed/renamed screen or a removed/renamed state — breaks the build-seed contract), MINOR (added screen/state/component), PATCH (polish/copy/token-value tweak); Keep-a-Changelog entry at the screen/state grain.
4. **Deprecate before removing** — deprecate a screen/state in a MINOR (note the replacement) before removing in a MAJOR; on removal, no dangling link/index/sibling reference remains.
5. **Re-capture screenshots** — any changed screen's screenshot is re-captured (no stale render — the rendered-truth analog of keeping a sketch in sync).
