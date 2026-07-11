# SVG integration and theming

Load when embedding SVGs (inline vs img vs Lottie), recoloring to design tokens, or
fixing illustrations for dark mode.

## Inline vs `<img>` vs sprite — the decision

| Mode | When | Trade-offs |
|---|---|---|
| **Inline React component** | Token recoloring needed; a11y attributes managed in JSX; small art on hot paths | Ships in the JS bundle; CSS reaches inside |
| **`<img src>`** | Larger static art; below-the-fold; no CSS reach needed | Cacheable + `loading="lazy"`; recolor must be baked into the file |
| Sprite/`<use>` | Many small repeated glyphs | Icon-system territory; rarely right for illustration |

Vite setup (with the SVGR plugin, `vite-plugin-svgr`):

```tsx
import EmptyProjects from "@/assets/illustrations/empty-projects.svg?react"  // component
import emptyUrl from "@/assets/illustrations/empty-projects.svg?url"          // URL string
// ?raw exists for the raw markup string (rarely needed for illustration)
```

- `?react` requires the plugin (it runs SVGR); `?url`/`?raw` are Vite built-ins. Add
  the plugin's type reference to `vite-env.d.ts` so TS accepts `?react` imports.
- Verify the suffix convention against the plugin's current docs at setup — it has
  changed across major versions.

## Sizing and layout shift

- Keep the `viewBox`. Inline components: drop the file's fixed `width`/`height` and
  size via CSS on the slot. `<img>` path: KEEP (or set on the element) `width`/`height`
  — the browser derives the aspect ratio from them and reserves space without extra
  CSS.
- The slot always reserves space: explicit height or `aspect-ratio` — an empty-state
  illustration that pops in and shoves the heading down is a CLS bug.
- Responsive: cap with `max-width` + `height: auto`; illustrations scale down
  gracefully, so one asset serves all breakpoints.

## Bundle discipline

- Inline SVG = JS bytes on every load of that chunk. Inline the small (≤ ~10 kB)
  empty-state art on hot paths; `?url` + `loading="lazy"` anything big or below the
  fold.
- Never import an illustration into a shared/global chunk it isn't used by; keep it in
  the route's module so code-splitting scopes it.

## Recoloring to tokens

Sourced SVGs hardcode their palette. For token-driven art:

1. Inline the SVG as a component.
2. Replace accent fills with CSS variables:

   ```svg
   <path fill="#6c63ff" .../>          →  <path style="fill: var(--primary)" .../>
   <rect fill="#f2f2f2" .../>          →  <rect style="fill: var(--muted)" .../>
   ```

3. Keep literal: skin tones, true blacks/whites that MUST stay (rare), brand marks.
4. `currentColor` works only for monochrome art (single fill) — multi-color
   illustrations need per-fill substitution.
5. Group repeated colors first (a quick find-by-hex pass); most library SVGs use 3-6
   distinct fills, so the edit is minutes, not hours.

Because the fills now reference semantic tokens, the SAME asset follows a theme
switch — this is the durable dark-mode strategy.

## Dark mode — three strategies

Most light-theme illustrations break on dark backgrounds: baked-in white shapes glow,
near-black strokes vanish, pastel accents lose contrast.

1. **Token-driven recolor (preferred):** as above — background shapes on
   `var(--muted)`-style tokens, strokes on foreground tokens. One asset, both themes.
2. **Per-theme asset pairs:** two exports (light/dark). Swap via the app's theme
   class/attribute when a manual theme toggle exists (the common product-app case);
   `<picture>` + `prefers-color-scheme` tracks only the OS setting, so it suits
   OS-driven theming only. Right when the art is too complex to tokenize or comes from
   an editor (Storyset) that can export both.
3. **Filter adaptation** (`filter: brightness()/invert()` on the container): limited —
   acceptable for monochrome line art, mangles multi-color scenes. Last resort.

Audit every illustration in BOTH themes at integration time; strategy is chosen per
asset class, not per app.

## Animated imagery (Lottie / animated SVG)

```tsx
import Lottie, { type LottieRefCurrentProps } from "lottie-react"
import { useEffect, useRef, useSyncExternalStore } from "react"
import emptyAnim from "@/assets/illustrations/empty-projects.json"

// Client-only (mark the file "use client" under an SSR framework).
let mql: MediaQueryList | undefined
const getMql = () =>
  (mql ??= window.matchMedia("(prefers-reduced-motion: reduce)"))
const subscribe = (cb: () => void) => {
  const m = getMql()
  m.addEventListener("change", cb)
  return () => m.removeEventListener("change", cb)
}
function useReducedMotion() {
  // lazy mql + module-scope subscribe: stable identities, SSR-safe import
  return useSyncExternalStore(
    subscribe,
    () => getMql().matches,
    () => false,   // server snapshot: assume no reduction until hydrated
  )
}

function EmptyState() {
  const reduced = useReducedMotion()
  const lottieRef = useRef<LottieRefCurrentProps>(null)
  // autoplay is only read at load — pause/play explicitly so a mid-session
  // preference change actually stops a running animation:
  useEffect(() => {
    if (reduced) lottieRef.current?.pause()
    else lottieRef.current?.play()
  }, [reduced])
  return (
    <Lottie lottieRef={lottieRef} animationData={emptyAnim}
            loop autoplay={!reduced}
            aria-hidden="true" style={{ height: 200 }} />
  )
}
```

- `lottie-react` is the common React wrapper (the `@lottiefiles/dotlottie-react` player
  is the vendor's current alternative — check which the project already uses before
  adding either).
- Reduced motion: render paused (static first frame) when the user prefers reduced
  motion. Gating `autoplay` covers only initial load — the explicit pause/play effect
  above is what honors a mid-session preference change. This is imagery's side of the
  reduced-motion contract; the motion-implementation skill owns the app-wide posture.
- Auto-playing motion running longer than 5 seconds total (looping or not) needs a
  visible pause control (WCAG 2.2.2) — play-once only avoids it when the animation
  finishes within 5 seconds.
- Animated SVG (Storyset export) embeds CSS/SMIL animation inside the file — it plays
  in `<img>` too, but reduced-motion gating then needs the CSS media query inside the
  SVG or an `<img>`-swap; prefer the Lottie path when you need control.
- Lottie JSON can be heavy (50-500 kB) — always lazy-load below-the-fold animations
  and consider the static-SVG fallback for the first paint.
