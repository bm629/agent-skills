# Render → vision-review loop + token-to-code mapping (depth)

Loaded on demand by `authoring-hi-fi`. Depth on the signature mechanism (the loop) and the token→code bridge.

## The render → vision-review → refine loop

The core mechanism. A hi-fi screen is produced by iterating, not by a single write:

1. **Generate** the screen's code (HTML+Tailwind, or React+shadcn) bound to the token map (below).
2. **Render headlessly** — load the code in a headless browser (`agent-browser`/Playwright) at each target viewport.
3. **Screenshot** — capture one image **per viewport × per state** (the matrix in the screenshot protocol below).
4. **Vision-review** the screenshot(s) against the DS + the wireframe + the Step-6 bar — what only a rendered pixel shows: does it render without breakage; does it match the wireframe structure; DS visual conformance (color/type/spacing/components); every state present; correct reflow at each viewport; numeric-WCAG signals (contrast, visible focus, target size); objective polish + the five aesthetic heuristics + legible hierarchy.
5. **Refine** the code to close any gap the vision review found; re-render; repeat.
6. **Bounded** (§9): cap the iterations (a small N, e.g. 3–4 per screen). If a screen still can't reach the bar — typically because the DS lacks a token the bar needs (a contrast-passing accent, a larger target token) — **stop and surface the blocker** as an assumption/gap (route a DS amend), ship the screen flagged, and do NOT keep spinning.
7. **Present** the refined screens + their screenshots for the human visual gate. Never present first-shot codegen or an un-rendered screen.

**Vision-capable-runtime prerequisite.** Steps 4 needs a runtime that can *see* the screenshot. A text-only runtime produces blind codegen — state the degradation explicitly and treat the run as un-reviewed; never fabricate "the render looks good".

**The reviewer re-renders too.** `reviewing-hi-fi` repeats steps 2–4 on its own (a fresh render), never trusting a handed-in screenshot — so the author's screenshots are evidence, not the gate.

### Grounding (the published design-to-code loop)

This mirrors the agentic design-to-code literature: ReLook's generate–diagnose–refine loop with a multimodal LLM as the visual critic ("scoring code with screenshots" + actionable vision-grounded feedback); Vision-Guided Iterative Refinement (condition the model on screenshots of the target AND its own render, prompt it to revise to match); DesignCoder's browser-screenshot self-inspection; UICoder's compile-render-CLIP feedback; VisRefiner's visual-difference learning; the Design2Code / Sketch2Code benchmarks; and UI2Code^N's finding that VLM-judge rankings track human evaluation. (See `sources.md`.)

## Screenshot-capture protocol

Capture the matrix the screen needs (proportional — a static single-viewport screen needs one):

- **Viewports:** content-driven, common starting points **360 / 768 / 1024 / 1280** (adjust where content cramps). Mobile target → a phone-frame mockup width.
- **States:** one capture per state the flow visits — **empty / loading / populated / error / success / partial**.
- Keep the screenshots with the artifact: they are the visual target the human gate approves and the build phase reuses.

## Token → code mapping (consume the design-system)

Map the design-system / W3C DTCG tokens into the code's theme layer **once**, then bind every value to it. DTCG tiers (primitive → semantic → component) are preserved in the mapping.

### CSS custom properties (the semantic layer)

```css
:root {
  --background: 0 0% 100%;
  --foreground: 222 47% 11%;
  --primary: 221 83% 53%;
  --primary-foreground: 0 0% 100%;
  --muted: 210 40% 96%;
  /* ...one per DS semantic token... */
}
.dark { --background: 222 47% 11%; --foreground: 210 40% 98%; /* overrides the same names */ }
```

### Tailwind utilities consume the tokens

- Tailwind v3: map in `tailwind.config` — `colors: { background: 'hsl(var(--background))', primary: 'hsl(var(--primary))', ... }`, then use `bg-background`, `text-primary`, etc.
- Tailwind v4: the `@theme` inline block binds the CSS vars to the utility namespace.
- shadcn (React stack): set `tailwind.cssVariables: true` in `components.json`; shadcn components already consume `background`/`foreground`/`primary`/… so overriding the CSS vars re-themes the whole UI without touching component classes. `.dark` does dark mode.
- Style Dictionary (v4+, DTCG support) can generate the CSS-var block from the DS's DTCG JSON.

### The conformance rule

Every visual value is **token-backed** — a Tailwind token-utility, a CSS var, or a shadcn token. A raw `#hex`, `12px`, or `bg-blue-500` that bypasses a token is **drift** (a `revise`). Fix a contrast/target failure by adjusting or adding a **token**, never by recoloring/​resizing one element off-token. A token the DS lacks is a surfaced gap → amend the DS, then consume it.

## Code-stack choice

- **Default: standalone HTML + Tailwind** (CDN or a minimal build) — portable, trivially headless-renderable, no toolchain assumption. Single-file is fine for a seed; data is mock/inline.
- **React + shadcn** when the project's build stack is React/Next — the seed sits close to the build target, so the build carries the components over instead of re-implementing them (the no-handoff / low-drift win).
- Either way the artifact must **render headlessly** (the loop's prerequisite) and stay a **seed** (no tests/real backend/routing beyond showing the screen).
