# Flow-level accessibility — depth

> Loaded for Workflow Step 7. Accessibility *of the flow* — can every persona,
> including assistive-technology users, **complete each path**? This is distinct from
> per-screen pixel accessibility (contrast, target size, focus *appearance*), which is
> the wireframes + design-system layer's job. Keep the boundary: F-flow = path
> completability; wireframes/DS = per-screen pixel WCAG.

## Why flow-level a11y is its own concern

A flow can be built from perfectly accessible screens and still be **uncompletable** by
an AT user — focus that doesn't move sensibly across steps, a step that only works with
a mouse gesture, an error the screen reader never announces, a route change that drops
the user's place. Walked with a keyboard and a screen reader, can this path be
*finished*? That is the question this step answers.

## The checks

### Keyboard operability + focus order through the flow (WCAG 2.2 SC 2.1.1, 2.4.3)

- **SC 2.1.1 Keyboard** — every step operable by keyboard alone, with **no keyboard
  trap**. "No exceptions for 'most users have mice'."
- **SC 2.4.3 Focus Order** — focus moves across steps in a **meaning-preserving order**
  (matching the logical/reading order). On a route or step change, focus is moved
  **deliberately** to the new step's main content/heading — not dropped, not left on the
  old (now-hidden) screen. A multi-step flow that advances a step but strands focus at
  the top is a flow-level focus-order defect. (SPA pattern: on route change, move focus,
  announce the navigation, keep a logical tab order after dynamic updates.)

### Screen-reader / AT completability of every path

Every path — happy AND unhappy — completable with a screen reader: the user can perceive
each step's purpose, the available branches, and **errors must be announced**
(programmatically determinable), not signalled by color/position alone. An error state
that is visually obvious but never announced strands the AT user on a path the sighted
user recovers from. The recovery path of the edge checklist must be reachable +
perceivable non-visually.

### No mouse-only / gesture-only required step

No step on a required path depends *solely* on hover, drag, or a complex gesture
(drag-only reorder with no keyboard alternative, hover-only reveal of a required
control, a multi-touch-only gesture). Each has a keyboard/AT-operable equivalent.

### Cognitive load, steps-to-completion & locale (proportional)

Inclusive design also means not overloading the user — but note: **path length /
steps-to-completion is judged once, by the flow-quality step (Step 8 / no-gratuitous-
step)**, not re-judged here (avoid double-jeopardy). This step's locale concern: where
the product is localized, navigation/flow *direction* respects RTL/bidi (the direction
of progress, the entry/exit affordances) — a navigational note, not pixel mirroring
(that's wireframes/DS). Explicitly n/a for a stated single-locale product (no
false-revise).

## The boundary (single-source discipline)

| Concern | Owned by |
|---|---|
| Path keyboard/AT-completable, focus-order across steps, no mouse-only, errors announced | THIS skill (flow-level) |
| Per-screen contrast (4.5:1 / 3:1), target size (24px), focus *appearance* (≥ thresholds), ARIA on a component | wireframes + design-system |
| Path length / steps-to-completion | flow-quality (Step 8), judged once |

## Sources

- WCAG 2.2 — SC 2.1.1 Keyboard (all functionality keyboard-operable, no traps); SC
  2.4.3 Focus Order (meaning-preserving focus sequence; manage focus on route change —
  move to main heading/content, announce navigation).
- SPA focus-management practice — move focus + announce on route/step change; maintain
  logical tab order after dynamic content updates.
- The per-screen pixel WCAG (contrast/target-size/focus-appearance) is the wireframes +
  design-system layer — referenced here only to mark the boundary, not re-taught.
