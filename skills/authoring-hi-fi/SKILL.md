---
name: authoring-hi-fi
description: >
  Use when authoring or amending a high-fidelity UI design AS CODE — each key
  screen realized as runnable code (standalone HTML+Tailwind by default,
  React+shadcn when the build stack is React), derived from upstream wireframes +
  design-system, rendered headlessly and screenshotted, used as a build SEED.
  Guides the METHOD, not the outline: deriving one screen per wireframe-named
  screen/state, consuming design-system tokens through a token-to-code map (never
  inventing a token or raw hex/px), realizing the visual language + objective
  polish + named aesthetic heuristics to real pixels, rendering real content +
  every state, running a bounded generate-render-screenshot-vision-review-refine
  loop, judging numeric WCAG 2.2 AA on the render, and amending as a scoped
  versioned delta. Composes with a template tool + agent-browser + shadcn +
  research. Requires a vision-capable runtime. Not for reviewing hi-fi, the screen
  structure (wireframes), the token system (design-system), or final code.
extensions:
  claude:
    when_to_use: "authoring or amending a hi-fi UI design as code from the upstream wireframes + design-system, via a render-vision-review loop"
    argument-hint: "<the upstream wireframes + design-system to realize as rendered hi-fi code; the build stack if known>"
version: "1.0.0"
forge:
  status: reviewed
  forged: 2026-06-14
  reviewed: 2026-06-14
---

# `authoring-hi-fi` — SKILL.md

> **Variant:** standard · **When to use:** producing (or amending) a high-fidelity UI design as runnable, rendered code from the upstream wireframes + design-system — a build seed an engineer can grow into production, gated on a human visual check.

## Overview

This skill is the *how-to* of producing strong, comprehensive **high-fidelity UI design as code** — the judgment a producer applies, not the section list. The artifact is **code that renders to pixels**: standalone HTML+Tailwind by default, **React+shadcn when the build stack is React** (so the seed sits close to the build target and minimizes drift). It assumes a **template tool** (section structure), a **headless browser** (`agent-browser`/Playwright, to render + screenshot), the product's **design-system** + **shadcn** (the token + component source of truth), and a **research capability**. The producer is handed the **upstream wireframes** (the screens + states + structure) and the **design-system** (the tokens + component contracts) and realizes every wireframe-named screen — never a blank page, never re-deciding structure.

The signature mechanism is a **loop, not a single write**: generate → render headlessly → screenshot (per viewport × state) → **vision self-review** against the DS + wireframe + the bar → refine → repeat to the bar → human visual gate. This **requires a vision-capable runtime**; a text-only run is blind codegen (degraded — say so, never fake a render).

Two boundaries keep this in lane: hi-fi owns **final visuals realized as pixels + the numeric pixel-WCAG judgment** (the wireframe only *reserved* these); it **consumes** the design-system's tokens (never invents/grades them); it renders the **given** wireframe structure (never re-decides layout/screens/nav); and it is a **build SEED** — intentionally thin (no tests, mock data, CDN fine, single-file fine) — not final production code (the build phase rebuilds the data layer, routing, state, tests, perf).

## When to activate

- Authoring a new hi-fi design as code from the upstream wireframes + design-system.
- Realizing the key screens (+ their states) a wireframes doc specifies, to rendered pixels.
- **Amending** an existing hi-fi when a token, screen, shared layout, or referenced component changes (see Step 8).
- Filling a hi-fi template with researched, rendered, decision-complete screens.

**Do NOT activate when:**

- Reviewing or grading a finished hi-fi → use `reviewing-hi-fi`.
- Producing the screen *structure* (layout regions, component selection, states-as-structure) → that is the upstream **wireframes**.
- Authoring/grading the **token system / component catalog** → that is the **design-system**; consume it here.
- Re-deciding which screens/transitions exist → that is **user-flows**.
- Writing final **production code** (tests, real backend, routing) → that is the build phase; this is a seed.

## Inputs

Read **every document the plan hands you** — your `depends_on` set (the typical upstreams: the **wireframes** that name + structure the screens, and the **design-system** that supplies tokens + component contracts). The named upstreams are guidance, not a precondition: be **self-contained** — produce from whatever you receive; when an expected upstream is absent, proceed on what you have and surface the gap as an assumption (Step 7), never fabricate. **Confirm the runtime can render + you can see the render** (a vision-capable runtime + a headless browser); if it cannot, say so and treat the run as degraded — do not present an unverified render as reviewed.

## Workflow

### Step 1: Take the structure from the template tool — don't invent an outline

Get the section structure from your hi-fi template tool (comprehensive variant). Do **not** restate a section list here; this skill supplies the method that *fills* those sections well. If none is available, obtain/forge a comprehensive hi-fi structure, then proceed.

### Step 2: Derive the screen set from the upstream wireframes

The hi-fi `depends_on` the wireframes. **Every wireframe-named screen, and every state the flow/wireframe visits, gets a rendered hi-fi screen.** Build the screen-inventory (each screen + its states + target viewports → its section) so coverage is auditable — this is also the amend-ripple surface (Step 8). A wireframe-named screen with no defined content is a gap — record it (Step 7), never invent it. Render the given structure; do not add screens/regions/nav the wireframe didn't name (an over-reach).

### Step 3: Set up the token → code map (consume the design-system; never invent)

Map the design-system / DTCG tokens into the code's theme layer **once**, then bind everything to it: semantic **CSS custom properties** (`--background`, `--primary`, … with a `.dark` override), consumed by **Tailwind utilities** (`hsl(var(--token))` in the config, or the v4 `@theme` block) and the **shadcn CSS-variable theme** on a React stack. Every visual value is **token-backed** — no raw `#hex` / `12px` / `bg-blue-500` that bypasses a token. A token/component the DS lacks is a **surfaced gap** (→ amend the DS), never inlined. (Depth: `references/render-loop-and-tokens.md`.)

### Step 4: Realize the visual language + polish to pixels

Turn the wireframe's structure + the DS tokens into a polished, real screen:

- **Visual execution** — token-backed color, real typography (type scale/weight/line-height/measure), the 8pt spacing cadence realized, elevation/shadow, radius, a real icon set, placeholder-safe imagery; the wireframe's *structural* hierarchy now expressed in real contrast/scale/weight/color/position.
- **Objective polish** (checkable) — aligned to the grid, consistent spacing scale, optical balance, no clipped/overlapping/orphaned elements, on-token values, consistent treatment across sibling screens.
- **The five named aesthetic heuristics** (the program's polish bar — judged, but each named + articulable; subjective out-of-set taste is NOT a requirement): **balance** (visual-weight distribution), **whitespace & restraint** (intentional negative space; not cramped, not over-decorated), **spacing rhythm** (a consistent, pleasing cadence), **focal clarity** (one clear emphasis the eye lands on), **aesthetic cohesion** (a "designed", intentional feel — not assembled-from-parts). (Depth + "what good looks like" per heuristic: `references/visual-a11y-and-amend.md`.)

### Step 5: Render real content + every state, then run the render→vision-review→refine loop

- **Real content** (no lorem) + realistic + **edge data** (long strings, overflow, empty, pluralization, i18n length) — lorem hides layout/overflow/tone/a11y problems.
- **Render every state** the flow visits, as actual pixels: empty (reason + guide-to-action), **loading = a skeleton mirroring the populated layout** (not a bare spinner), populated, error (plain-language cause + recovery), success (what changed + next step), partial.
- **Run the loop:** generate the code → render it headlessly (`agent-browser`) → screenshot **per viewport × state** → **vision-review** the screenshot against the DS + wireframe + the Step-6 bar → refine → repeat. **The loop is bounded** (§9): cap the iterations; if a screen still can't reach the bar (e.g. a missing DS token caps contrast), **stop and surface the blocker** as an assumption/gap — do not spin. Present the *refined* screens + their screenshots, never first-shot codegen.

### Step 6: Self-check against the bar before handing off

Confirm all hold (this is the bar `reviewing-hi-fi` asserts — same list, single-sourced, each proportional to the screen's archetype):

1. **Full coverage** — every wireframe-named screen + state is rendered (no orphans vs the wireframes).
2. **Fidelity + scope** — hi-fidelity visuals (not wireframe-grey), no invented structure/nav/token, and it's a *seed* (not over-built, not claimed production-ready).
3. **Visual execution + hierarchy** — DS visual language realized; primary element visually dominant; hierarchy legible.
4. **Polish** — the objective subset + the five named heuristics hold; subjective out-of-set taste is not imposed.
5. **Token-backed** — every value token-backed (Tailwind/CSS-var/shadcn); no raw off-token value; mapping faithful to the DS.
6. **Rendered + self-reviewed** — every screen renders without breakage and was vision-reviewed against the wireframe + DS through the loop.
7. **Content realism** — real content, no lorem; edge data exercised.
8. **Rendered states** — each flow-visited state rendered, skeleton-not-spinner, error = cause + recovery.
9. **Responsive** — rendered + verified at the target viewports; mobile content-priority + adaptive nav where form-factor matters.
10. **Numeric WCAG 2.2 AA on the render** — contrast 4.5/3:1 (SC 1.4.3/1.4.11), focus visible + not-obscured (2.4.7/2.4.11) + appearance ≥2px/3:1 (2.4.13, house rule), target ≥24px (2.5.8), keyboard, reduced-motion; axe-core clean with no rule disabled.
11. **DS conformance** — no drift/override; a missing token/component surfaced, not inlined.
12. **Gaps surfaced** — undefined screen/content, missing DS element, a degraded (no-render) run = explicit assumptions.
13. **Versioned (on amend)** — the doc's own version + changelog reflect the change (Step 8).

### Step 7: Surface gaps explicitly

A wireframe-named screen with undefined content, an element needing a token/component the DS lacks, a contrast/target failure the tokens can't satisfy, or a degraded (text-only, no render) run → an **open question or assumption**. List it; flag missing tokens/components for the design-system owner. Never paper a gap with an invented token/component or a faked screenshot (§7).

### Step 8: Amend mode — edit + re-render the delta, don't redraw (when iterating)

When handed an existing hi-fi + a change, treat it as a **scoped, versioned diff**, never a regenerate:

1. **Scope + ripple** — identify the touched screen(s)/state(s), then trace the ripple: every screen consuming a **changed DS token** through the token→code map (the distinctive wide hi-fi ripple), every screen reusing a changed **shared layout/component**, every screen added/removed by an upstream **wireframe** change, every screen naming a **changed/deprecated DS component**.
2. **Edit + re-render the delta** — minimal in-place edit; untouched screens' **code** stays byte-stable + their **screenshots are not re-captured** (not byte-diffed — headless renders aren't byte-identical run-to-run); **re-render + re-vision-review ONLY the delta**; a **token change is applied once in the map** then re-rendered across all consumers in one pass (the one legitimate wide ripple), never hand-edited per screen.
3. **Version + changelog** — bump the **doc's own** version: MAJOR (removed/renamed screen or a removed/renamed per-screen state — breaks the build-seed contract), MINOR (added screen/state/component), PATCH (polish/copy/token-value tweak); Keep-a-Changelog entry at the screen/state grain.
4. **Deprecate before removing** — mark a screen/state deprecated in a MINOR (note the replacement) before removing in a MAJOR; on removal confirm no link/index/sibling reference remains and prune.

## Rules

**Hard rules (never violate):**

- **One rendered screen per wireframe-named screen/state.** Coverage is keyed to the wireframes; an un-rendered named screen is incomplete.
- **Consume the design-system; never invent.** Token-backed values only — no raw hex/px; a missing token/component is a flagged gap, not an inline one-off.
- **Render the given structure.** Lay out the wireframe's screens; never re-decide structure or navigation.
- **Run the loop, bounded.** Generate→render→screenshot→vision-review→refine before handing off; cap iterations + surface the blocker rather than spin (§9).
- **It's a seed, not production.** No tests/real backend required; never claim production-readiness; the build phase hardens it.
- **Real content, never lorem.** Real + edge data; lorem is a defect at hi-fi.
- **Numeric a11y on the render, never disable a rule.** Fix contrast/focus/target at the token layer; a suppressed axe rule is a finding.
- **Vision-capable runtime, or say so.** A text-only run is degraded; surface it, don't fake a screenshot.
- **Compose, don't duplicate.** Take the section structure from the template tool.
- **Surface gaps, don't invent.** Undefined screen/content, missing token/component, degraded run = explicit assumption.
- **Amend, don't regenerate.** Edit + re-render the delta + version + changelog; never re-render untouched screens.

**Preferences (override-able):**

- Default standalone HTML+Tailwind; switch to React+shadcn when the build stack is React.
- "Comprehensive" sets *ambition* but stay **proportional** — a thin static screen has fewer states + no responsive/interactivity work.
- Prefer a skeleton-that-mirrors-the-layout over a bare spinner where the layout is known.
- The five aesthetic heuristics are judged but named + articulable — don't impose a personal hue/layout preference.

## Gotchas

- **Blind codegen.** Producing code without rendering + seeing it is the #1 failure — the loop (Step 5) is the value; a text-only run is degraded, say so.
- **Off-token raw values.** A `#3b82f6` / `13px` that bypasses the token map is drift — bind everything to the DS tokens (Step 3).
- **Lorem ipsum.** Placeholder text hides overflow/tone/a11y problems and signals an unfinished design — render real content.
- **Treating the seed as production.** Adding tests/real backends (over-build) or claiming prod-ready (over-claim) — it's a seed; the build hardens it.
- **Disabling an axe rule to go green.** Excluding `color-contrast` hides a real defect — fix the token, document a genuine exception.
- **Inventing a missing component.** A component the DS lacks is a gap for the DS owner, not an inline improvisation.
- **Re-deciding structure.** Adding a screen/region/nav the wireframe didn't name oversteps into the wireframe's lane.
- **Token-change drift on amend.** Hand-editing a token's value per screen instead of once in the map is the most common amend regression — change it once, re-render all consumers.

## Anti-patterns

- **"The code looks right, ship it."** UI isn't done until you render + look — run the loop.
- **"I'll use a nice blue here."** Off-token — bind to the DS token or flag the gap.
- **"Lorem ipsum is fine for now."** It hides the real layout — use real + edge content.
- **"I'll wire the backend + add tests."** Over-building a seed — keep it thin; the build hardens it.
- **"axe flags contrast; I'll exclude that rule."** Fix the token; never disable a real rule.
- **"The wireframe is vague, I'll add a screen."** Surface it as an assumption instead.
- **"It's a small token tweak, I'll regenerate everything."** Amend: change the token once + re-render only its consumers + version + changelog.

## Output

A **comprehensive, rendered high-fidelity UI design as code** that meets the **Step 6 bar** (full coverage vs the wireframes; hi-fidelity + seed scope; visual execution + legible hierarchy; objective + named-heuristic polish; token-backed/no-drift; rendered + vision-reviewed; real content; rendered states; responsive; numeric WCAG 2.2 AA on the render; DS conformance; gaps surfaced; versioned on amend). Each screen is **runnable code + the rendered screenshots per viewport × state**. The **abstract consumer** is the human visual gate + the build phase (which grows the seed into production) and a reviewer (which asserts the same bar). The doc's *structure* comes from the template tool; this skill supplies the *content quality*.

**Worked example (the loop in one screen).** Hand-off: a wireframe "Projects — list" (states: populated, empty, loading, error) + a design-system with `--primary`, `--muted`, a `Card`, a `Button`, a `Table`. Method: map the tokens into a Tailwind/CSS-var theme (Step 3); build the populated screen with a real `Table` of representative projects (real names/dates, one long-name row for overflow), the empty state ("No projects yet" + a "New project" `Button` on `--primary`), a skeleton mirroring the table for loading, and an error card ("Couldn't load projects — Retry"); render at 360/768/1024/1280, screenshot each state; vision-review → catch that the empty-state CTA is `--muted` on white at 2.9:1 → fix by binding it to `--primary` (a token, not a one-off) → re-render → now 4.8:1; axe clean. Result: four rendered states, token-backed, WCAG-passing — a seed the build can grow. (Negative contrast caught by the loop, fixed at the token layer — not by recoloring one button off-token.)

## Related

- A **hi-fi template tool** (a content/template gateway) — supplies the comprehensive per-screen section structure this skill fills.
- **`agent-browser`** (+ `playwright-best-practices`) — renders + screenshots the code for the loop; this skill drives it, doesn't re-teach it.
- **`shadcn`** + **`ui-ux-pro-max`** / **`ckm-*`** — the React component theming + visual-execution guidance; composed-with, not re-taught.
- A **deep-research capability** — grounds visual + interaction decisions.
- **`reviewing-hi-fi`** — asserts the same bar (re-renders + vision-reviews); author + reviewer share one bar so they don't drift.
- The **upstream wireframes** (a `depends_on` document) — the screen structure to realize.
- The **design-system** (a `depends_on` document) — the tokens + component contracts to consume; it owns the per-component a11y contract, this skill verifies the rendered result conforms.

## Progressive disclosure

- `references/render-loop-and-tokens.md` — the render→vision-review→refine loop procedure + the screenshot-capture protocol (viewport × state) + the DS/DTCG→Tailwind/CSS-var/shadcn token-mapping recipe + the code-stack choice. Load when setting up the loop or the token map.
- `references/visual-a11y-and-amend.md` — the five aesthetic heuristics ("what good looks like" each) + visual-execution depth + the numeric WCAG 2.2 SCs + axe setup + the amend token-ripple/versioning procedure. Load for a polish/a11y pass or an amend.
- `references/sources.md` — research provenance for the method + the bar (load only to audit where the guidance came from).

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap).
- Body ≤ ~500 lines / 5,000 tokens.
- Heavy content lives in `references/`, loaded on demand.
