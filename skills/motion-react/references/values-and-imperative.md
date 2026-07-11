# Motion values and imperative animation

Load for motion values, derived transforms/springs, imperative sequences, or animated
number tickers (stat tiles, counters).

## Motion values — updates without re-renders

```tsx
import { motion, useMotionValue, useTransform, useSpring } from "motion/react"

const x = useMotionValue(0)
const opacity = useTransform(x, [-200, 0, 200], [0, 1, 0])
const smoothX = useSpring(x, { stiffness: 300, damping: 30 })

<motion.div drag="x" style={{ x, opacity }} />
<motion.div style={{ x: smoothX }} />   // a sprung follower of the dragged value
```

- A motion value updates the DOM **without triggering a React re-render** — the whole
  point. High-frequency values (drag position, scroll, animated numbers) stay off the
  render path.
- `useTransform(value, inputRange, outputRange)` derives one value from another;
  `useTransform(value, v => f(v))` for arbitrary mapping.
- `useSpring(source, config)` returns a sprung follower of another motion value (or a
  static target set via `.set()`).
- Subscribe with `useMotionValueEvent(value, "change", v => ...)` — also
  `"animationStart"` / `"animationComplete"` / `"animationCancel"`. Never read `.get()`
  during render and expect it to stay current.

## Imperative animation — `animate()` and `useAnimate`

```tsx
import { useAnimate, stagger } from "motion/react"

const [scope, animate] = useAnimate()

async function onSave() {
  await animate(scope.current, { scale: [1, 1.04, 1] }, { duration: 0.25 })
  await animate("li", { opacity: 1 }, { delay: stagger(0.05) })
}
```

- `useAnimate` gives a `scope` ref and an `animate` function whose selectors resolve
  inside the scope — the tool for event-driven sequences that don't map to declarative
  state.
- The standalone `animate(target, keyframes, options)` (import from `"motion/react"` or
  the framework-agnostic `"motion"`) also accepts a motion value or a plain number as
  target — which enables tickers, below.
- Returned animations are promise-like: `await` sequences instead of nesting callbacks.

## Animated number ticker (stat tiles)

```tsx
import { useMotionValue, useTransform, useReducedMotion, animate, motion } from "motion/react"
import { useEffect } from "react"

function Ticker({ value }: { value: number }) {
  const count = useMotionValue(value)   // start at the real value: no replay on remount
  const rounded = useTransform(count, v => Math.round(v).toLocaleString())
  const shouldReduceMotion = useReducedMotion()

  useEffect(() => {
    if (shouldReduceMotion) { count.set(value); return }
    const controls = animate(count, value, { duration: 0.6, ease: "easeOut" })
    return () => controls.stop()
  }, [value, shouldReduceMotion, count])   // count is stable; listed for exhaustive-deps

  return <motion.span>{rounded}</motion.span>
}
```

- A `motion` element renders a motion-value child directly and updates it outside React —
  no re-render per frame.
- Cleanup (`controls.stop()`) prevents orphaned animations on unmount/re-target.
- Reduced motion: imperative `animate()` is **not** governed by `MotionConfig
  reducedMotion` (it runs outside that React context) — gate it yourself:
  `useReducedMotion() ? count.set(value) : animate(count, value, ...)`. This applies to
  every `animate()`/`useAnimate` sequence, not just tickers.
- Format inside the transform (`toLocaleString`, units) so the rendered text is final.

## Drag beyond reorder

For free-form drag (bounded cards, drag-to-dismiss sheets) — drag-to-reorder lists use
the `Reorder` components instead (see the layout reference):

```tsx
<motion.div
  drag="y"
  dragConstraints={{ top: 0, bottom: 0 }}   // or a ref to a bounding element
  dragElastic={0.2}                          // give beyond constraints (0–1)
  dragMomentum={false}                       // no inertia after release
  onDragEnd={(e, info) => {
    if (info.offset.y > 120 || info.velocity.y > 500) dismiss()
  }}
/>
```

- `onDragEnd` receives `info.offset` (total delta) and `info.velocity` — threshold on
  both so a fast flick dismisses even with a short offset.
- `useDragControls` starts a drag from a different element (a handle):
  `const controls = useDragControls()` → `dragControls={controls}` on the draggable +
  `onPointerDown={e => controls.start(e)}` on the handle.
- Accessibility: drag is **pointer-only** — always pair a drag interaction with a
  keyboard-accessible alternative (a dismiss/close button, move actions), same rule as
  `Reorder`.
- Anything beyond these props (axis locking nuance, `dragSnapToOrigin`, transforms of
  drag listeners) — consult the live gestures docs rather than guessing.

## When NOT to use these

- A value that changes once per user action and can re-render normally → plain state.
- Scroll-linked storytelling effects (`useScroll` + long transforms) → wrong genre for
  product UI; see the docs if a marketing surface genuinely needs it. Two product-legit
  scroll-linked exceptions ARE sanctioned one-liners — a reading-progress bar:
  `const { scrollYProgress } = useScroll()` →
  `<motion.div style={{ scaleX: scrollYProgress, originX: 0 }} />`
  (the `originX: 0` matters — the default transform origin is center, so the bar would
  grow outward from the middle),
  and a condensing header (`useTransform(scrollY, [0, 80], [64, 44])` on its height) —
  don't hand-roll scroll listeners for those; consult the live docs for `useScroll`'s
  options beyond this.
