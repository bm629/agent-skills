# Layout animations and shared elements

Load when animating layout changes (size/position), shared-element transitions, or list
reordering.

## The `layout` prop

```tsx
<motion.div layout />
```

Any layout change caused by a React render — flex order, grid placement, size change from
content, a sibling appearing — animates automatically. Motion measures the before/after
layout and animates via CSS `transform` (translate + scale), never by animating
width/height, so it avoids main-thread layout work and can skip paint entirely.

- `layout="position"` — animate only position, snap size. Use for elements whose aspect
  ratio must not stretch (images, video, text blocks that would distort).
- Trigger discipline: the animation fires on render — batch state changes so one render
  produces the final layout, not a cascade of intermediate ones.

## Distortion correction

Scale-based animation distorts children and rounded corners:

- Give directly-affected **children their own `layout` prop** so they counter-scale
  instead of stretching.
- Set `borderRadius` and `boxShadow` **via `style`** (or animate them) — Motion
  scale-corrects these properties automatically only when it controls them:
  `style={{ borderRadius: 12 }}`.

## `layoutId` — shared-element transitions

```tsx
import { AnimatePresence, motion } from "motion/react"

{items.map(item => (
  <motion.div layoutId={`card-${item.id}`} key={item.id} onClick={() => open(item)} />
))}

<AnimatePresence>
  {selected && <motion.div layoutId={`card-${selected.id}`} className="detail" />}
</AnimatePresence>
```

When a new element mounts with a `layoutId` matching one that exists (or just unmounted),
it animates **from the old element's bounds to its own** — the card-grows-into-detail,
active-tab-underline-slides, thumbnail-to-lightbox pattern.

- The classic sliding-indicator: render the underline/highlight inside the active item
  only, with a constant `layoutId="indicator"`; switching items animates it across.
- Pair the closing side with `AnimatePresence` so the reverse transition plays.

## `LayoutGroup`

```tsx
import { LayoutGroup } from "motion/react"

<LayoutGroup>
  <Accordion />
  <Accordion />
</LayoutGroup>
```

Components that affect each other's layout but don't re-render together (one accordion
opening pushes the next down) need grouping so all members re-measure when any of them
changes. Also namespaces `layoutId`s (`<LayoutGroup id="a">`) when the same ids repeat
across siblings.

## Reordering lists

- `layout` on every row + stable keys → programmatic reorder (sort, filter) animates
  automatically.
- Removal + reflow: wrap rows in `<AnimatePresence mode="popLayout">` — exiting rows pop
  out of the flow (absolutely positioned; parent must not be `position: static`) while
  siblings animate into place; combine `exit` + `layout` on each row.
- **Drag-to-reorder: use the purpose-built `Reorder` components — never hand-roll it**
  from `drag` + `layout` + hit-testing:

  ```tsx
  import { Reorder } from "motion/react"

  <Reorder.Group axis="y" values={items} onReorder={setItems}>
    {items.map(item => (
      <Reorder.Item key={item.id} value={item}>{item.label}</Reorder.Item>
    ))}
  </Reorder.Group>
  ```

  `Reorder.Group` takes the array + setter (`values` / `onReorder`); each `Reorder.Item`
  binds one `value`. Items are `motion` components underneath, so they compose with
  `layout`, `exit`/`AnimatePresence`, and `whileDrag`. Give each `Reorder.Item`
  `position: relative` (or `absolute`) — the automatic z-index lift on the dragged item
  depends on it; without it the dragged row renders under its siblings.
  **Accessibility caveat: `Reorder` (and `drag` generally) is pointer-only — there is no
  keyboard path.** Always pair drag-driven reordering with a keyboard-accessible
  alternative (move up/down buttons or a menu action on each row).

## Performance notes

- Layout animation measures the DOM — cheap for tens of elements, measurable for hundreds.
  For big virtualized tables, animate only what enters the viewport, or skip layout
  animation entirely.
- Reduced motion: under `MotionConfig reducedMotion="user"` with the OS preference set,
  layout (and transform) animations are disabled automatically — never rely on a layout
  animation to communicate something with no non-animated fallback.
