# Composition & states — depth reference

> Depth for `authoring-wireframes` Steps 4–5. Load when composing a non-trivial or data-dense screen. Portable; provenance in `sources.md`.

## Layout grid + spacing cadence (structure, not pixels)

- Set the **column structure** (commonly a 12-col content grid; fewer for narrow surfaces) and a **spacing cadence intent** — an **8pt** rhythm (or **4pt** for dense data UI). 8 divides cleanly into common screen sizes and across pixel densities.
- The wireframe states the *cadence + structure*; the **design-system owns the exact px token values**. A raw `13px` is both off-cadence and a hi-fi overshoot.
- Use spacing to express grouping: the **internal-≤-external** rule (space within a group < space between groups) makes the grouping read (Gestalt proximity).

## App-shell / page-frame consistency

- Define ONE shared header / nav / container / max-width once; every screen sits in it. No per-screen full-bleed left-aligned dumps.
- The shell is a single shared region — it is the **amend-ripple surface**: a change to it must reach every screen that reuses it (see `a11y-and-amend.md`).

## Visual hierarchy as structure

- Order content by visual priority driven by the screen's **primary task**.
- **Gestalt proximity** → which elements group into a card/region. **Scanning patterns**: F-pattern for text-dense content, Z-pattern for sparse/landing — place the primary content + CTA on the scan path. Keep the primary task + CTA **above the fold**.
- Never a raw vertical pile of undifferentiated sections — group into cards/panels with headings + spacing rhythm.

## Objective layout-quality bar (subjective taste excluded)

Every screen composes to this objective bar; a reviewer checks it as one condition (subjective "a nicer layout exists" is NOT a gap):

1. **Primary action on the scan path** (F/Z) — the main CTA is where the eye lands, above the fold.
2. **Related elements grouped** (Gestalt proximity / internal-≤-external).
3. **No gratuitous region/element** — every region earns its place (minimalism).
4. **Sibling-screen consistency** — like screens use like layouts; shared regions are identical.

## Density & whitespace strategy

- Choose a density appropriate to the surface: tight-but-consistent (4/8/12 rhythm) for dashboards/tables; more breathing room for marketing/onboarding.
- Density is **consistent** within a screen and across like screens; whitespace separates groups + sets rhythm (a structural tool, not leftover space).

## Data-display patterns (data-dense screens)

- **Display choice:** table vs list vs cards — deliberate, with a reason.
- **Table controls:** columns; **sort** (control in the column header + arrow indicator); **filter** (dropdown by category); **pagination** (a bar when data exceeds one view); **row-density** (e.g. tall/normal/short/compact); **sticky header**; **row-expansion** for detail.
- **Progressive disclosure:** start with the essential controls (search, sort); defer secondary detail behind accordion / disclosure / tooltip / show-more / expandable row / "Advanced".
- **Forms:** group fields; persistent labels (not placeholder-as-label); **structured inputs** — never require a normal user to hand-author a serialized `key=value`/CSV/JSON string (offer a raw/advanced escape only where the audience allows). Translate the data model into input affordances.

## Per-screen state quality (not just presence)

- **Loading** — a **skeleton mirroring the populated layout** beats a bare spinner where the layout is known: it tells the user what to expect, cuts perceived load ~30%, prevents layout shift. A bare global spinner is the common anti-pattern.
- **Empty** — explain **why** it's empty + **what to do** (the create/find CTA), plain language. Distinguish first-run empty vs filtered-to-zero vs error-empty.
- **Error** — plain language (no raw codes), **what went wrong + how to recover**; specify placement, inline vs blocking, the retry/next affordance.
- **Success/confirmation** — what changed + the next step (state-changing screens). An async action is trigger → in-progress → **success | error**, all enumerable.
- **Partial** — some-data / degraded / slow-network where the path visits it.
- **State ↔ flow** — the states a screen documents trace to the states the upstream flow's path actually visits for that screen.
