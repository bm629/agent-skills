# Ecosystem integration and testing

Load when combining Motion with Radix/shadcn, Tailwind, or a client-side router; when
using AutoAnimate; or when testing components that animate.

## Radix / shadcn components

Radix primitives (Dialog, Popover, Accordion, Select — what shadcn/ui wraps) expose
`data-state="open|closed"` attributes and ship CSS-driven open/close animations in the
shadcn styles. Two integration modes:

1. **Keep the CSS tier (default).** The shipped `data-state` keyframes are usually
   enough; don't replace working CSS with Motion for its own sake. Add
   `motion-reduce:` variants to any custom `data-state` CSS.

2. **Motion-driven exit (when you need real exit choreography):** Radix suspends unmount
   while a CSS `data-state` animation plays — that is exactly how shadcn's
   `data-[state=closed]:animate-out` close animations work with no extra wiring. What it
   cannot wait for is a **JS-driven** (Motion) exit animation. For those, use the
   primitive's `forceMount` prop so the node stays mounted, and let `AnimatePresence`
   own mount/unmount:

   ```tsx
   import { useState } from "react"
   import { AnimatePresence, motion } from "motion/react"
   import * as Dialog from "@radix-ui/react-dialog"

   const [open, setOpen] = useState(false)

   <Dialog.Root open={open} onOpenChange={setOpen}>
     <Dialog.Trigger>Open</Dialog.Trigger>
     <Dialog.Portal forceMount>
       <AnimatePresence>
         {open && (
           <Dialog.Content asChild forceMount>
             <motion.div initial={{ opacity: 0, scale: 0.97 }}
                         animate={{ opacity: 1, scale: 1 }}
                         exit={{ opacity: 0, scale: 0.97 }} />
           </Dialog.Content>
         )}
       </AnimatePresence>
     </Dialog.Portal>
   </Dialog.Root>
   ```

   Drive `open` from the Radix `onOpenChange` so state stays in React. The recipe
   generalizes to any Radix primitive (Tabs, Accordion, Popover): `forceMount` keeps the
   node mounted unconditionally, so the visibility conditional (e.g.
   `active === value && ...`) moves inside the force-mounted node, wrapped by
   AnimatePresence. Two things the fragment above elides: `Dialog.Overlay` unmounts immediately on close too — give it
   the identical `asChild forceMount` + AnimatePresence treatment or it pops out while
   the content animates; and strip shadcn's `data-state` animation classes
   (`data-[state=...]:animate-*`) from any part Motion now drives, or the two tiers
   double-animate.

## Tailwind boundaries

- Tailwind `transition-*` / `animate-*` utilities own the CSS tier (hover, focus, simple
  data-state); Motion owns the JS tier (exit, orchestration, layout, values). Don't
  double-animate the same property from both.
- Tailwind classes style `motion.*` elements normally — `<motion.div className="...">`.
- Duration/easing tokens: define once (CSS variables or the Tailwind theme) and reference
  from both tiers so the app has one motion language.

## Router page transitions (TanStack Router / react-router)

The naive pattern — `AnimatePresence` around a keyed wrapper containing a live
`<Outlet />` — is broken in practice: during the exit, the still-mounted outgoing wrapper
re-renders its live `Outlet` against the already-updated router state, so the exiting
view shows the NEW route's content (or blank) while it animates out. **Freeze the
outgoing view's content:**

```tsx
import { useState } from "react"
import { AnimatePresence, motion } from "motion/react"
import { useLocation, useOutlet } from "react-router"

// Capture the outlet element once per route mount.
function FrozenRoute() {
  const outlet = useOutlet()
  const [frozen] = useState(outlet)   // never updates after mount
  return <>{frozen}</>
}

const location = useLocation()        // inside the layout component

<AnimatePresence mode="wait">
  <motion.div
    key={location.pathname}
    initial={{ opacity: 0, y: 4 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0 }}
    transition={{ duration: 0.15 }}
  >
    <FrozenRoute />
  </motion.div>
</AnimatePresence>
```

- TanStack Router: same principle — freeze the **resolved** matched content on mount,
  not the `<Outlet />` element. Capturing `useState(<Outlet />)` does NOT work: the
  element still resolves its match from live router context at render time and shows
  the new route's content mid-exit. Consult the TanStack Router docs for the
  outlet-capture mechanism on your version.
- react-router offers two distinct working alternatives: (1) the `FrozenRoute` capture
  above — `useOutlet()` returns the already-resolved child element, so freezing it in
  state truly freezes the content; (2) skip freezing and render
  `<Routes location={rememberedLocation}>` — the remembered location keeps the old
  match rendering during the exit.
- Key the wrapper by the route path — the key change is what triggers exit/enter.
- Scope: this covers client-side SPA routers. **Next.js App Router is not covered** —
  its navigation unmounts segments in a way that defeats AnimatePresence exit
  animations, and the frozen-outlet trick does not map; it needs framework-specific
  workarounds.
- `mode="wait"` keeps one view at a time; keep it fast (≤ 200 ms) — page transitions are
  the easiest place to make an app feel slower.
- Subtle opacity(+small y) is the product-appropriate default; full slides are marketing
  genre. Under reduced motion this degrades to a fade automatically via
  `MotionConfig reducedMotion="user"`.

## Direction-aware exits (carousels, wizards, paginated views)

Exiting components can't receive prop updates, so the direction must flow through
AnimatePresence's `custom` prop (which reaches exiting children), with variant functions
resolving per-direction values. Note the two `custom` locations: on `AnimatePresence`
for the **exiting** child, on the `motion` element for the **entering** one.

```tsx
import { AnimatePresence, motion } from "motion/react"

const slide = {
  enter: (dir: number) => ({ x: dir > 0 ? 40 : -40, opacity: 0 }),
  center: { x: 0, opacity: 1 },
  exit: (dir: number) => ({ x: dir > 0 ? -40 : 40, opacity: 0 }),
}

<AnimatePresence mode="wait" custom={direction} initial={false}>
  <motion.div key={step} custom={direction} variants={slide}
              initial="enter" animate="center" exit="exit"
              transition={{ duration: 0.2 }} />
</AnimatePresence>
```

Keep the travel small (tens of px) and remember reduced motion degrades this to a fade
automatically under `MotionConfig reducedMotion="user"`.

## AutoAnimate — the one-line list tier

```tsx
import { useAutoAnimate } from "@formkit/auto-animate/react"

const [parent] = useAutoAnimate()
<ul ref={parent}>{items.map(i => <li key={i.id} />)}</ul>
```

- Package `@formkit/auto-animate` (MIT). Animates child **add / remove / move** on the
  ref'd parent. Zero config; options exist (e.g. `useAutoAnimate({ duration: 150 })`);
  the hook's second value toggles animations on/off.
- Respects `prefers-reduced-motion` automatically — no extra wiring.
- Reach for it when a list only needs add/remove/move; upgrade to Motion
  (`AnimatePresence` + `layout`) when you need custom exit choreography, shared elements,
  or coordination with other animated values. Don't run both on the same list.

## Testing animated components

**Unit/component (vitest/Jest + RTL, jsdom):**

```ts
// test setup file
import { MotionGlobalConfig } from "motion/react"
MotionGlobalConfig.skipAnimations = true
```

- Animations complete instantly; assert **end states** (visibility, text, class), never
  mid-flight values or timing.
- jsdom has no `window.matchMedia` — stub it in the setup file or `useReducedMotion`
  and `MotionConfig reducedMotion="user"` paths throw or silently test nothing:

  ```ts
  Object.defineProperty(window, "matchMedia", {
    writable: true,
    value: vi.fn().mockImplementation((query: string) => ({
      matches: false,   // true to exercise the reduced-motion branch
      media: query,
      addEventListener: vi.fn(), removeEventListener: vi.fn(),
      addListener: vi.fn(), removeListener: vi.fn(), dispatchEvent: vi.fn(),
    })),
  })
  ```

  To exercise the reduced branch, return `matches: true` for
  `prefers-reduced-motion` — or leave that assertion to the Playwright
  `reducedMotion: "reduce"` e2e below.
- jsdom has no real layout: layout animations, `whileInView`, and measurements don't run
  meaningfully — unit-test the state logic and leave visual verification to e2e.
- Components inside `AnimatePresence` unmount asynchronously even with skipped
  animations in some paths — prefer `await waitForElementToBeRemoved(...)` over expecting
  synchronous removal.

**E2E (Playwright):**

- `reducedMotion: "reduce"` in the browser context stabilizes screenshots and flows, and
  doubles as the reduced-motion behavioral test — assuming the app sets
  `reducedMotion="user"` per this skill; an app that doesn't honor the preference keeps
  animating regardless. A working fallback there: inject CSS that disables
  animations/transitions via `addInitScript`/`addStyleTag` — `MotionGlobalConfig` is a
  bundled module export, not a window global, so an init script can only reach it if
  the app deliberately exposes it in test builds.
- For full-motion runs, use auto-waiting assertions (`toBeVisible`) rather than fixed
  sleeps; animation timing is the classic flake source.
- Axe-based a11y scans don't judge motion — the reduced-motion check is a behavioral
  assertion you write, not an axe rule.
