# Empty-state craft and imagery accessibility

Load when building empty states / onboarding / error pages, or wiring imagery
accessibility.

## The empty-state anatomy

```
        [ illustration ]           <- supports, never dominates (~160-240px desktop)
        No projects yet            <- headline: state the situation, plainly
   Projects appear here once you   <- one or two lines: why it's empty +
   create or import one.              what will change that
        [ Create project ]         <- the primary action (when one exists)
```

- The text carries the message; the illustration carries the tone. If the illustration
  disappeared, the state must still fully work.
- One primary action, maybe one secondary link — an empty state is not a menu.
- Vertical-center in the content region; generous whitespace; the illustration sits
  above the headline.

## The four variants — different messages, same family

| Variant | The message | Action |
|---|---|---|
| **First-run** (never had data) | Welcome/orientation: what lives here, why it's useful | The create/import/connect primary action |
| **Cleared** (had data, now none) | Neutral: "all done" / "nothing left" — can be a positive (inbox zero) | Usually none, or the create action quietly |
| **No results** (filter/search) | The QUERY produced nothing — not that the space is empty | Clear/adjust filters; never hide the search box |
| **Error** (couldn't load) | Something failed — say so honestly, not "no items" | Retry; support link if persistent |

Never show the first-run art/copy for a failed load — mislabeling an error as
emptiness destroys trust in the data.

Consistency: all empty states in an app use the same illustration family, the same
scale, the same anatomy. A screen-by-screen mix of sizes and styles reads as neglect.

## Onboarding and error pages

- Onboarding/first-run moments: same anatomy, warmer copy; imagery earns more room
  here than anywhere else. Shows once — don't re-decorate a screen the user visits
  daily.
- Error pages (404/500/permission): illustration softens, copy stays honest and
  actionable (what happened, what to do, where to go). Keep the app shell/nav when
  possible so the user isn't stranded.

## Accessibility contract for imagery

**Decorative (the default for empty-state/onboarding/error art):** the adjacent text
carries the meaning, so the image is hidden from assistive tech —

- Inline SVG: `aria-hidden="true"` on the `<svg>` (or its wrapper), AND strip or blank
  any `<title>`/`<desc>` inside the file (downloaded SVGs often ship
  `<title>undraw_xyz</title>` — announced by AT if `aria-hidden` is ever dropped, and
  shown as a browser hover tooltip regardless).
- `<img>`: `alt=""` (empty alt, not a missing alt).
- Lottie/animated wrappers: `aria-hidden="true"` on the container.

**Informative (the image itself adds information the text doesn't):** real `alt` text
(or `role="img"` + `aria-label` on inline SVG) describing the information, not the
picture ("Chart trending upward" not "Illustration of a person with a chart").

**Animated imagery:**

- `prefers-reduced-motion: reduce` → static first frame: gate `autoplay` AND pause a
  running instance when the preference changes mid-session (gating alone covers only
  initial load — worked snippet in the integration reference).
- Auto-starting motion lasting more than 5 seconds TOTAL — looping or not — needs a
  user-visible pause/stop control when shown alongside other content, which UI imagery
  always is (WCAG 2.2.2; the reduced-motion preference does not substitute for it).
  Play-once avoids the requirement only when its total duration is ≤ 5 seconds.
- Nothing flashes more than 3 times/second (WCAG 2.3.1).

**Contrast:** decorative art is exempt from contrast minima, but any imagery that
carries meaning (a diagram, an illustrated instruction) needs its meaningful parts to
meet non-text contrast (WCAG 1.4.11) in BOTH themes.

## Copy notes (microcopy for these states)

- Headline states the situation ("No projects yet"), not an apology.
- Body says why + what changes it. No jargon, no exclamation-mark cheer on error
  states.
- Buttons name the act ("Create project"), not "Get started".
