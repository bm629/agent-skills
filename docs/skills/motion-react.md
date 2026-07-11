# motion-react

> Implement animation in a React SPA with **Motion** (the framer-motion successor:
> npm package `motion`, import `motion/react`) — core enter/exit animation,
> variants + stagger orchestration, AnimatePresence (modes, keys, direction-aware
> exits), layout + `layoutId` shared-element transitions, motion values +
> imperative animation (number tickers, drag), `Reorder` drag-to-reorder — with
> reduced-motion accessibility as a first-class requirement, compositor-friendly
> performance discipline, motion restraint for data-dense product UI, a
> choosing-the-tool framework (plain CSS/Tailwind + Radix `data-state` for simple
> toggles, AutoAnimate for list add/remove, Motion for the rest), Radix/shadcn +
> router integration, and deterministic tests.

**Skill file:** [`skills/motion-react/SKILL.md`](../../skills/motion-react/SKILL.md)
**Version:** 1.0.0

## Purpose

Motion is the JS-lifecycle animation tier a React product UI reaches for when CSS can't
express the job: exit animations on unmount, orchestrated sequences, shared-element
moves, springs, number tickers, drag. This skill teaches the current library idioms
(the rename story, `delayChildren: stagger()` since 12.22.0, `motion.create()`), and it
refuses to let animation ship without three non-negotiables: reduced-motion support
(the four-layer contract below), transform/opacity-only performance, and restraint
(purposeful, ≤400 ms, one motion language). Just as important, it teaches when NOT to
use Motion — most hover/focus styling belongs in CSS, and most internal-tool list
transitions are a one-line AutoAnimate ref.

## When to activate

- ✅ Adding enter/exit/list animations, page/view transitions, shared-element moves, animated counters, or gesture feedback to a React SPA.
- ✅ Migrating or writing code that references `framer-motion` (the old package name).
- ✅ Wiring reduced-motion support or auditing existing animation for accessibility/performance.
- ✅ Choosing between Motion, CSS/Tailwind transitions, and AutoAnimate for a given interaction.

### When NOT to activate

- Animated illustrations / Lottie files — imagery, not UI motion (`ui-illustrations` owns it).
- Video rendering (Remotion) or scroll-storytelling/parallax marketing pages — different genre.
- Deciding a specific product's motion design language — that is a design-system decision; this skill supplies the vocabulary and constraints.

## What it covers

- **The rename + install story:** `motion` package, `motion/react` import, React 18+;
  `LazyMotion` + `m` (`motion/react-m`) bundle reduction (~34 kB → ~4.6 kB initial);
  RSC `"use client"` note.
- **Choosing the tool:** the decision table — CSS/Tailwind + Radix `data-state` default
  for simple state toggles; AutoAnimate (`@formkit/auto-animate`) for list
  add/remove/move; Motion for exit/orchestration/shared-element/values/drag; View
  Transitions API named for awareness.
- **Core animation:** `initial`/`animate`/`exit`, tween-vs-spring (incl. duration-based
  springs), keyframes, `whileHover`/`whileTap`/`whileFocus`/`whileInView`.
- **Variants + orchestration:** propagation, dynamic variants, `when`,
  `delayChildren: stagger()` (with the 12.22.0 version floor and the deprecated
  `staggerChildren` migration note).
- **AnimatePresence:** stable-key requirement, `sync`/`wait`/`popLayout` modes,
  in-place content swaps (skeleton→content), direction-aware exits via
  `custom` + `usePresenceData`.
- **Layout animations:** `layout`, `layoutId` shared elements, `LayoutGroup`,
  distortion correction, `Reorder.Group`/`Reorder.Item` for drag-to-reorder (with the
  pointer-only a11y caveat), list reflow with `popLayout`.
- **Motion values + imperative:** `useMotionValue`/`useTransform`/`useSpring`,
  `useAnimate`/`animate()`, the animated number-ticker pattern (reduced-motion-gated,
  no remount replay), free-form drag (`dragConstraints`, `onDragEnd`
  offset+velocity thresholds, `useDragControls`), sanctioned `useScroll` one-liners
  (progress bar with `originX: 0`, condensing header).
- **Reduced-motion accessibility (the four-layer contract):** `MotionConfig
  reducedMotion="user"` at the root; `useReducedMotion` component overrides;
  imperative `animate()` is NOT governed by MotionConfig and needs an explicit gate;
  CSS-side motion needs the media query / Tailwind `motion-reduce:`. WCAG 2.3.3 +
  2.2.2 mapped precisely.
- **Restraint for product UI:** durations (150–300 ms micro, ≤200 ms route swaps),
  purpose test, one motion language as tokens, user-initiated vs system/data-driven
  trigger tiebreaker.
- **Integration:** Radix/shadcn (`forceMount` + AnimatePresence for JS-driven exits —
  incl. the Overlay and the double-animation trap; Radix waits for CSS `data-state`
  animations on its own), Tailwind tier boundaries, router page transitions (the
  frozen-outlet pattern — a live `<Outlet />` inside the exiting view renders the NEW
  route's content; Next.js App Router explicitly scoped out).
- **Testing:** `MotionGlobalConfig.skipAnimations` in the setup file, end-state
  assertions, the jsdom `matchMedia` stub (inlined), Playwright
  `reducedMotion: "reduce"`.

## Structure

- `SKILL.md` — the worked core path, the tool-choice table, rules/gotchas/anti-patterns.
- `references/layout-and-shared-elements.md` — layout, layoutId, LayoutGroup, Reorder.
- `references/values-and-imperative.md` — motion values, tickers, drag, useScroll exceptions.
- `references/a11y-and-restraint.md` — the four-layer reduced-motion contract, WCAG mapping, restraint tokens.
- `references/integration-and-testing.md` — Radix/Tailwind/router seams, AutoAnimate, direction-aware exits, test setup.
- `references/sources.md` — research provenance (motion.dev docs, the published package types, the changelog).

## Provenance

Forged 2026-07-11 via the skill-forge pipeline against live motion.dev docs, the
published `motion@12.42.x` package, and the upstream changelog; every API fact
multi-verified across 14 fresh-reviewer cycles (5 forge self-review + 9 verification),
each a cold subagent fact-checking against the live sources plus adversarial
behavioral simulations.
