---
name: motion-react
description: >
  Use when adding animation to a React app with the Motion library (the framer-motion
  successor: npm package `motion`, import `motion/react`) — enter/exit animations,
  variants and stagger, AnimatePresence, layout and shared-element transitions,
  animated number tickers, gesture states — or when deciding whether a job needs
  Motion at all versus plain CSS/Tailwind transitions or AutoAnimate. Covers
  reduced-motion accessibility (MotionConfig, useReducedMotion, WCAG 2.3.3/2.2.2)
  as a first-class requirement, performance discipline (transform/opacity only),
  motion restraint for data-dense product UI, Radix/shadcn and router integration,
  and keeping tests stable (MotionGlobalConfig.skipAnimations). Keywords: motion,
  framer-motion, animation, AnimatePresence, layout animation, micro-interactions,
  reduced motion, page transitions, stagger, spring.
extensions:
  claude: {}
  copilot: {}
  cursor: {}
  gemini: {}
  codex: {}
version: "1.0.0"
forge:
  status: reviewed
  forged: 2026-07-11
  reviewed: 2026-07-11
---

# motion-react — Motion for React

## Overview

Implements UI animation in React with **Motion** — the library previously published as
`framer-motion`, independent since late 2024 and published as the npm package `motion`
(import from `"motion/react"`). The skill covers the DOM product-UI animation surface:
declarative enter/exit, variant orchestration, layout and shared-element transitions,
motion values and number tickers, and gesture states — with three non-negotiables woven
through: **reduced-motion accessibility**, **compositor-friendly performance**, and
**restraint** (purposeful, short, consistent motion — especially in data-dense tools).
It also owns the "do I even need Motion?" decision: many jobs are better served by plain
CSS or a one-line AutoAnimate call.

## When to activate

- ✅ Adding enter/exit/list animations, page or view transitions, shared-element moves, animated counters, or gesture feedback to a React SPA.
- ✅ Migrating or writing code that references `framer-motion` (the old package) — this skill teaches the current `motion` idioms.
- ✅ Wiring reduced-motion support, or auditing existing animation for accessibility/performance.
- ✅ Choosing between Motion, CSS/Tailwind transitions, and AutoAnimate for a given interaction.

**Do NOT activate when:**

- The task is animated illustrations / Lottie files — that is imagery, not UI motion (a dedicated illustrations skill owns it).
- The task is video rendering (Remotion) or scroll-storytelling/parallax marketing pages — different genre; only `whileInView` basics are covered here.
- The product's motion design language (which durations/easings a specific app adopts) is being decided — that is a design-system decision; this skill supplies the vocabulary and constraints.

## Workflow

### Step 1: Choose the right tool — most animations don't need Motion

| Job | Reach for | Why |
|---|---|---|
| Hover/focus color, opacity, small scale | Plain CSS / Tailwind `transition-*` | Zero JS, zero bundle, GPU-friendly |
| Open/close styling on Radix-based components (accordions, popovers, dialogs) | CSS keyed off Radix `data-state` attributes | The primitive already exposes state; CSS animates it |
| List add / remove / reorder in an internal tool | AutoAnimate — one `useAutoAnimate()` ref on the parent | Zero-config, animates child add/remove/move, respects `prefers-reduced-motion` automatically |
| Exit animations on unmount, orchestrated sequences, shared-element moves, springs, number tickers, drag / drag-to-reorder (`Reorder` components) | **Motion** | Needs JS lifecycle control CSS cannot express |
| Browser-native view morphs (same-document, or cross-document/MPA) | View Transitions API | Named for awareness; for view/route swaps in a React SPA, AnimatePresence covers the equivalent (whole-document morphs like a theme crossfade remain VTA-only) |

Escalate down the table only when the simpler tier genuinely cannot do the job.

### Step 2: Install and set the app-level posture

```bash
npm install motion
```

```tsx
import { motion, MotionConfig } from "motion/react"

// App root — respect the user's OS reduced-motion setting everywhere:
<MotionConfig reducedMotion="user">
  <App />
</MotionConfig>
```

- Package is `motion`; React entry is `"motion/react"`. React 18+ (docs state 18.2; the
  peer range is `^18.0.0 || ^19.0.0`). Anything importing
  `framer-motion` is the pre-rename package — same lineage, but new projects use `motion`
  and current docs/idioms live under that name.
- `MotionConfig reducedMotion` accepts `"user"` (respect the OS setting), `"always"`
  (force-reduce; debugging), `"never"` (default). Under reduction, Motion disables
  transform and layout animations while keeping opacity/color animations — usually exactly
  the right degradation. Set `"user"` at the root as the default posture; see
  `references/a11y-and-restraint.md` for the full contract.
- The reduced-bundle wiring is one wrapper:
  `<LazyMotion features={domAnimation} strict><m.div animate={{ opacity: 1 }} /></LazyMotion>`.
- React Server Component frameworks: `motion` components are client components — add a
  `"use client"` boundary (or import from `motion/react-client`); a plain Vite SPA needs
  neither.
- Bundle-sensitive apps: `LazyMotion` + the `m` component (`import * as m from
  "motion/react-m"`) renders for ~4.6 kB initially (vs ~34 kB for full `motion`), with
  features (`domAnimation`) loaded sync or — for the full saving — async after
  hydration; `strict` on `LazyMotion` throws if a full `motion` component sneaks in.

### Step 3: Core animation

```tsx
<motion.div
  initial={{ opacity: 0, y: 8 }}
  animate={{ opacity: 1, y: 0 }}
  exit={{ opacity: 0 }}
  transition={{ duration: 0.2, ease: "easeOut" }}
/>
```

- `initial` → `animate` runs on mount; `exit` runs on unmount **only inside
  `AnimatePresence`** (Step 5).
- `transition` picks the model: `type: "tween"` (duration + easing — UI default) or
  `type: "spring"` (physical; use for gestures/drag, sparingly for entrances). Keyframes:
  pass arrays (`animate={{ x: [0, 100, 0] }}`); `null` as the first keyframe means
  "current value".
- Gesture states: `whileHover`, `whileTap`, `whileFocus`, `whileDrag`, `whileInView` —
  values revert when the gesture ends. Prefer CSS for hover-only styling (Step 1); use
  these when the gesture must coordinate with other animated values.
- Product-UI durations: 150–300 ms for micro-interactions, ≤ 400 ms for larger
  transitions. Longer reads as lag, not polish.

### Step 4: Variants — orchestrate parent and children

```tsx
import { motion, stagger } from "motion/react"

const list = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { when: "beforeChildren", delayChildren: stagger(0.05) },
  },
}
const item = { hidden: { opacity: 0, y: 4 }, visible: { opacity: 1, y: 0 } }

<motion.ul variants={list} initial="hidden" animate="visible">
  {rows.map(r => <motion.li key={r.id} variants={item} />)}
</motion.ul>
```

- Variant names flow down: children with `variants` animate when the parent's state
  changes — no prop drilling.
- Orchestration lives in the parent's `transition`: `when: "beforeChildren" |
  "afterChildren"`, and **`delayChildren: stagger(interval)`** — the current idiom,
  available since `motion` 12.22.0 (`staggerChildren`/`staggerDirection` were
  deprecated in 12.21.0). On older installs (`framer-motion`, early 12.x) `staggerChildren:
  0.05` still works and `stagger()`-in-`delayChildren` is not supported (the option was
  a plain number there) — bump the package before migrating the idiom.
- Dynamic variants: a variant can be a function of `custom` (e.g. per-index delay).

### Step 5: AnimatePresence — exit animations

```tsx
import { AnimatePresence, motion } from "motion/react"

<AnimatePresence mode="popLayout">
  {rows.map(r => (
    <motion.div key={r.id} exit={{ opacity: 0, x: -8 }} layout />
  ))}
</AnimatePresence>
```

- Works by watching its **direct children**; every child needs a **stable, unique `key`**
  (array indices break exit animations — the classic failure).
- `mode`: `"sync"` (default — in/out simultaneously), `"wait"` (out fully before in; one
  child at a time — right for view/route swaps), `"popLayout"` (exiting elements pop out
  of layout flow so siblings reflow — right for lists; the parent needs non-`static`
  `position`).
- In-place content swaps (skeleton→content, tab panels): with `"wait"`, match the two
  children's dimensions or the gap flashes; when dimensions differ, crossfade in place
  via `"popLayout"` or a grid-stack/absolute overlay — and pair the container with
  `layout` if the size change itself should animate rather than snap.
- `initial={false}` skips mount animation for children present at first render.
  `onExitComplete` fires when all exits finish.
- Exiting components cannot receive prop updates — for direction-aware exits (carousels,
  paginated views), pass the direction via AnimatePresence's `custom` prop and read it
  with `usePresenceData` (or variant `custom`) inside the child.
- AnimatePresence must wrap the conditional — never be inside it.

### Step 6: Beyond the core — load the reference that matches the job

- Layout animations, `layoutId` shared elements, `LayoutGroup`, distortion fixes →
  `references/layout-and-shared-elements.md`
- Motion values, `useTransform`/`useSpring`, imperative `animate()`/`useAnimate`,
  animated number tickers for stat tiles → `references/values-and-imperative.md`
- The full reduced-motion contract, WCAG mapping, reduce-vs-keep table, motion-restraint
  tokens → `references/a11y-and-restraint.md`
- Radix/shadcn integration (`forceMount`), Tailwind boundaries, router page transitions,
  the AutoAnimate worked example, and testing (`MotionGlobalConfig.skipAnimations`,
  Playwright reduced-motion) → `references/integration-and-testing.md`

## Rules

**Hard rules (never violate):**

- **Respect reduced motion.** Every Motion-using app sets `MotionConfig reducedMotion="user"`
  (or an equivalent explicit strategy) at the root. Never ship large translations, zooms,
  parallax, or auto-playing motion that ignores the OS preference (WCAG 2.3.3; autoplaying
  >5 s motion needs a pause control per WCAG 2.2.2).
- **Animate `transform` and `opacity`, not layout-inducing properties.** Never animate
  `width`/`height`/`top`/`left`/margins directly — use the `layout` prop (which animates
  via transforms) or scale; cheap non-layout properties (color/background, SVG stroke
  values) are fine. Scale-based fills (progress bars, meters) need an explicit transform
  origin (`originX: 0` for a left-anchored fill) — the default is center. **One sanctioned exception:** expand/collapse reveals
  (accordion, disclosure) animate `height: 0 ↔ "auto"` with `overflow: hidden` — scale
  distorts text and `layout` can't clip-reveal; keep it short and user-initiated. Note
  reduced motion does NOT auto-reduce it (only transform/layout animations are
  disabled) — if the reveal displaces substantial content, gate it with
  `useReducedMotion()` to snap open instead.
- **Stable keys inside AnimatePresence.** Array indices as keys silently break exit
  animations.
- **Import from `"motion/react"`.** Do not add `framer-motion` to a new project; do not
  mix both packages.
- **Motion must be purposeful.** Animation communicates state change, spatial
  relationship, or feedback — decorative-only animation in a product UI is a defect, not
  polish.

**Preferences (override-able):**

- Micro-interactions 150–300 ms; route/page swaps ≤ 200 ms; other view-level
  transitions ≤ 400 ms (the outer bound, not the target).
- Tweens for UI state changes; springs for gesture-driven/physical interactions.
- Centralize durations/easings as design tokens rather than scattering literals.
- Prefer the simplest sufficient tier (Step 1) before reaching for Motion.

## Gotchas

- **Exit animation never plays:** the element isn't a direct child of `AnimatePresence`,
  its key is unstable, or the `AnimatePresence` itself unmounts with the element. Fix the
  tree, not the animation.
- **Old-package drift:** tutorials and LLM completions frequently emit `framer-motion`
  imports, `staggerChildren`, or `motion(Component)`-era idioms. Current: `motion` pkg,
  `delayChildren: stagger()`, and `motion.create(Component)` to wrap a custom component
  (it must expose its ref — `forwardRef` on React 18, the plain `ref` prop on React 19);
  check the live docs when an API looks dated.
- **`popLayout` needs positioning:** exiting elements are absolutely positioned; a
  `static`-positioned parent misplaces them.
- **Layout animation distorts rounded corners/shadows:** set `borderRadius`/`boxShadow`
  via `style` (or animate them) so Motion can scale-correct; give stretching children
  their own `layout` prop.
- **Springs on mount feel bouncy-slow:** physics-configured springs
  (stiffness/damping) derive their own settle time and ignore duration expectations;
  use a duration-based spring (`type: "spring", duration, bounce`) or a 200 ms tween
  for entrances.
- **Motion values don't re-render React:** rendering `{x.get()}` in JSX goes stale —
  render the motion value as a `motion` element child or subscribe via
  `useMotionValueEvent`.
- **Tests hang or flake on animations:** set `MotionGlobalConfig.skipAnimations = true`
  in the test setup and assert end-states (see the integration reference).
- **jsdom has no layout:** layout animations and `whileInView` need real measurements;
  unit-test the state logic, e2e-test the visuals.

## Anti-patterns

- **"Animate everything — it looks premium."** Data-dense tools earn polish through a few
  consistent, short, purposeful animations; motion noise slows comprehension.
- **"Skip reduced-motion for now, add it later."** It's a root-level one-liner when done
  first and an audit when done later. There is no "later".
- **"Just animate the height."** Layout properties jank on the main thread; `layout` prop
  or a different design.
- **"AutoAnimate is beneath us — rewrite the list in Motion."** If add/remove/move is all
  the list needs, one ref beats thirty lines of variants.
- **"Copy the framer-motion snippet from that 2023 blog post."** Verify against current
  docs; the package, imports, and stagger idiom changed.

## Output

Working animation code in a React codebase: components using `motion/react` primitives
(or deliberately simpler tiers per the Step-1 table), an app-level reduced-motion posture,
and test setup that keeps animated components deterministic. Consumers are the codebase's
reviewers and test suite — animation that ships with accessibility, performance, and
restraint already satisfied.

## Related

- A UI/UX design-guidelines skill (e.g. one carrying animation duration/meaning rules) is
  the METHOD source for when/what to animate; this skill is the implementation
  counterpart.
- A component-styling skill (Radix/Tailwind) owns the `data-state` CSS tier of the Step-1
  table.
- A router skill (e.g. TanStack Router) owns route structure; this skill only wraps route
  views for transitions.
- An illustrations skill owns Lottie/animated imagery — adjacent, not this skill's
  surface.
- A component-testing skill owns the RTL/vitest harness this skill's testing guidance
  plugs into.

## Progressive disclosure

- `references/layout-and-shared-elements.md` — load when animating layout changes, shared
  elements (`layoutId`), or reordering lists.
- `references/values-and-imperative.md` — load for motion values, transforms/springs,
  imperative sequences, or animated number tickers.
- `references/a11y-and-restraint.md` — load when wiring reduced-motion, auditing
  accessibility, or defining motion tokens/restraint rules.
- `references/integration-and-testing.md` — load when combining Motion with Radix/shadcn,
  Tailwind, or a router, when using AutoAnimate, or when tests involve animated
  components.
- `references/sources.md` — research provenance; load only when auditing claims.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap).
- Body ≤ ~500 lines / 5,000 tokens soft target; overflow lives in `references/`.
