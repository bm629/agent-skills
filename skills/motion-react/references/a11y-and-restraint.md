# Reduced-motion accessibility and motion restraint

Load when wiring reduced-motion support, auditing animation accessibility, or defining an
app's motion tokens/restraint rules.

## Why this is non-negotiable

Vestibular disorders make large-scale motion (parallax, zooming, sliding panels)
physically nauseating; every major OS ships a "reduce motion" setting that sites must
honor. The relevant WCAG 2.2 success criteria:

- **2.3.3 Animation from Interactions (AAA):** motion animation triggered by interaction
  can be disabled unless essential. Respecting `prefers-reduced-motion` is the standard
  implementation.
- **2.2.2 Pause, Stop, Hide (A):** moving/blinking/scrolling content that starts
  automatically and lasts more than 5 seconds needs a user control to pause/stop/hide
  it; **auto-updating** content (live tickers, refreshing data) needs such a control (or
  an update-frequency control) regardless of duration. The reduced-motion preference
  does not substitute for these controls.

## The four-layer contract

1. **App root — the default posture:**

   ```tsx
   <MotionConfig reducedMotion="user">
   ```

   Values: `"user"` (respect the OS setting), `"always"` (force-reduce — debugging or a
   user-profile "minimal motion" toggle), `"never"` (default). Under reduction Motion
   automatically disables **transform and layout** animations while preserving
   **opacity / color** animations — state changes stay communicated, spatial motion goes.
   Caveat for the profile-toggle path: `useReducedMotion()` reads only the OS media
   query, so an app using `reducedMotion="always"` must gate its override/imperative
   tiers with `useReducedMotionConfig()` (same import; respects the MotionConfig value,
   returns `boolean | null`) instead — an undocumented export as of v12; re-verify it on
   major upgrades. Durable fallback that needs no undocumented API: hold the app's
   minimal-motion toggle in your own state/context and gate the override + imperative
   tiers on that state directly.

2. **Component-level overrides where the default degradation isn't right:**

   ```tsx
   import { useReducedMotion } from "motion/react"

   const shouldReduceMotion = useReducedMotion()
   const slide = shouldReduceMotion ? { opacity: [0, 1] } : { x: [-40, 0], opacity: [0, 1] }
   ```

   Returns `boolean | null` from the live media query (null until it resolves, e.g. a
   first server-side render — treat null as no-reduction). Use it to swap a translation
   for a fade, set a ticker instantly, or gate video autoplay.

3. **Imperative animation (`animate()` / `useAnimate`) is NOT covered by MotionConfig** —
   it runs outside the React context that carries the setting. Gate it explicitly:

   ```tsx
   import { animate, useReducedMotion } from "motion/react"

   const shouldReduceMotion = useReducedMotion()
   if (shouldReduceMotion) count.set(target)
   else animate(count, target, { duration: 0.6 })
   ```

   Any imperative sequence that moves things spatially needs this gate; a reduced-motion
   audit that only checks `MotionConfig` misses this whole tier.

4. **CSS-side motion (Tailwind transitions, Radix data-state animations) is NOT covered
   by MotionConfig** — pair it with the media query:

   ```css
   @media (prefers-reduced-motion: reduce) {
     .animated-thing { transition: none; animation: none; }
   }
   ```

   Tailwind: the `motion-reduce:` / `motion-safe:` variants (`motion-reduce:transition-none`).

## Reduce vs keep

| Reduce / remove | Keep (safe) |
|---|---|
| Large translations, slide-ins across the viewport | Opacity fades |
| Zoom/scale on large surfaces | Color/background transitions |
| Parallax, scroll-linked movement | Small local feedback (≤ a few px) when essential |
| Auto-playing looping motion | Instant state changes |
| Layout reflows animating across the screen | Focus outlines, non-animated affordances |

A dialog that fades in under reduced motion still communicates the state change the
fly-up animation carried — degradation should preserve meaning, not remove feedback.

## Testing the preference

- DevTools → Rendering → "Emulate CSS media feature prefers-reduced-motion".
- Playwright: `reducedMotion: "reduce"` in context options — assert the reduced behavior
  in at least one e2e.
- `MotionConfig reducedMotion="always"` as a quick manual audit switch.

## Motion restraint for data-dense product UI

Method rules (a UI/UX guidelines skill is the canonical source; implementation summary):

- **Durations:** 150–300 ms micro-interactions; ≤ 400 ms view transitions. Under ~100 ms
  reads as instant; over ~400 ms reads as lag.
- **Purpose test:** every animation must communicate state change, spatial relationship,
  or feedback. If removing it loses no information and no feedback, remove it.
- **One motion language:** one or two easings and a small duration set, centralized as
  tokens — e.g. CSS variables (`--motion-fast: 150ms; --motion-base: 250ms;`) or a shared
  `transition` object passed via `MotionConfig transition={...}` — never per-component
  literals.
- **Where motion belongs** in a dashboard-like tool: entrances of transient surfaces
  (dialogs, toasts, popovers), list add/remove, state/feedback cues (save success,
  check pulse), tab/nav indicators, number tickers. **Where it doesn't:** persistent data
  surfaces (tables re-sorting on live data), anything the user reads while it moves,
  decorative ambience. The trigger is the tiebreaker: animate **user-initiated** changes
  (the user filtered/sorted/reordered — motion is feedback); never animate
  **system/data-driven** changes to a surface the user is reading (live re-sorts,
  polling updates). Applied to tickers: tick on user-initiated load/navigation; on
  background polls set the value instantly (and remember WCAG 2.2.2 — continuously
  auto-updating content needs an update control).
- **Interruptibility:** animations must never block input; Motion animations are
  interruptible by default — keep them that way (avoid `await`-gating user input on an
  animation).
