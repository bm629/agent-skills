# authoring-hi-fi

Author (or amend) a **high-fidelity UI design AS CODE** — every key screen realized as runnable code (standalone HTML+Tailwind by default, React+shadcn when the build stack is React), derived from the upstream wireframes + design-system, rendered headlessly, screenshotted, and handed off as a build SEED. The how-to (the render→vision-review loop + the token-to-code discipline), composed with a hi-fi template tool, `agent-browser`, `shadcn`, and research. Requires a vision-capable runtime.

## Purpose

A wireframe reserves the visuals; a design-system supplies the tokens; neither realizes a screen to pixels. This skill is the how-to layer that turns the wireframe's structure + the DS tokens into a polished, accessible, rendered screen an engineer can grow into production. Its signature mechanism is a **loop, not a single write**: generate → render headlessly → screenshot (per viewport × state) → vision self-review against the DS + wireframe + the bar → refine → repeat to the bar → human visual gate. The artifact is code that renders to pixels, intentionally thin (no tests, mock data, CDN fine) — a build seed, not final production code.

## When to activate

- ✅ Authoring a new hi-fi design as code from the upstream wireframes + design-system.
- ✅ Realizing the key screens (+ their states) a wireframes doc specifies, to rendered pixels.
- ✅ **Amending** an existing hi-fi when a token, screen, shared layout, or referenced component changes.
- ✅ Filling a hi-fi template with researched, rendered, decision-complete screens.

### When NOT to activate

- **Reviewing or grading a finished hi-fi** → `reviewing-hi-fi`.
- **Producing the screen structure** (layout regions, component selection, states-as-structure) → `authoring-wireframes`.
- **Authoring/grading the token system / component catalog** → `authoring-design-system` (consume it here).
- **Re-deciding which screens/transitions exist** → `authoring-user-flows`.
- **Writing final production code** (tests, real backend, routing) → that is the build phase; this is a seed.

## Method

Take the section structure from the hi-fi template tool (don't invent an outline). Derive the screen set from the upstream wireframes — every wireframe-named screen, and every state the flow visits, gets a rendered hi-fi screen. Set up a **token → code map once** (semantic CSS custom properties → Tailwind utilities / shadcn CSS-variable theme) and bind every visual value to it — no raw hex/px that bypasses a token. Realize the visual language + objective polish + the **five named aesthetic heuristics** (balance, whitespace & restraint, spacing rhythm, focal clarity, aesthetic cohesion). Render real content (no lorem) + edge data + every state (empty / loading-as-skeleton / populated / error / success / partial), then run the **render→vision-review→refine loop bounded** — surface the blocker rather than spin. On an amend, treat it as a scoped, versioned diff: edit + re-render only the delta (a token change applied once in the map, re-rendered across all consumers), version + changelog, deprecate before removing.

## What it produces

A comprehensive, rendered high-fidelity UI design as code that meets the **14-point self-check bar** (the same bar `reviewing-hi-fi` asserts): full coverage vs the wireframes; hi-fidelity + seed scope (not over-built, not claimed production-ready); visual execution + legible hierarchy; objective + named-heuristic polish; token-backed / no DS drift; rendered + vision-reviewed; real content; rendered states; responsive at the target viewports; numeric WCAG 2.2 AA on the render (axe-core clean, no rule disabled); DS conformance; gaps surfaced; versioned on amend; capability boundary respected. Each screen is runnable code + the rendered screenshots per viewport × state.

## Output

A **comprehensive, rendered hi-fi UI design as code** — runnable code plus the screenshots per viewport × state. The abstract consumer is the human visual gate + the build phase (which grows the seed into production) and a reviewer (which asserts the same bar). The doc's structure comes from the template tool; this skill supplies the content quality.

## Key guarantees

- **Renders + looks, never blind codegen** — the loop (render → screenshot → vision-review → refine) is the value; a text-only run is degraded, and it says so rather than faking a screenshot.
- **Consumes the design-system; never invents** — token-backed values only, no raw hex/px; a missing token/component is a flagged gap for the DS owner, not an inline one-off.
- **Renders the given structure** — lays out the wireframe's screens; never re-decides layout or navigation.
- **It's a seed, not production** — no tests/real backend required; never claims production-readiness; the build hardens it.
- **Numeric a11y on the render, never disable a rule** — fix contrast/focus/target at the token layer.
- **Amends, never regenerates** — edits + re-renders the delta, versions + changelogs; a token change is applied once in the map, not hand-edited per screen.
- **capability-record-aware** — when a `capability_record` is injected by the caller, the scope boundary (interior only vs system shell) is drawn from it; graceful fallback when absent.

## License

MIT © 2026 Bhushan Modi.
