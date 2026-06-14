# Sources & provenance — `reviewing-hi-fi`

Portable provenance for the review bar (single-sourced from `authoring-hi-fi` — same bar, judged on the render). Triangulated across reputable independent sources; nothing operational lifted.

## The bar is single-sourced from the author
The 13 conditions are the (reviewing+both) projection of `authoring-hi-fi`'s Step-6 bar — produce-bar and review-bar are one bar so they can't drift. See the `authoring-hi-fi` sibling's `references/sources.md` for the full method provenance.

## Re-render + vision-review (don't trust the image)
- The render→diagnose→refine + VLM-as-judge design-to-code literature: ReLook (MLLM visual critic scoring code with screenshots), Vision-Guided Iterative Refinement (condition on the rendered output), DesignCoder (browser-screenshot self-inspection), UI2Code^N (VLM-judge rankings track human evaluation). The reviewer applies the same render+vision discipline as a fresh, independent pass.
- "Verify visually, not via a DOM proxy" — a getComputedStyle/DOM read is not a substitute for rendering + looking; the reviewer re-renders and screenshots.

## Numeric WCAG 2.2 AA (on the render)
- W3C WCAG 2.2 — SC 1.4.3 (4.5:1 / 3:1), 1.4.11 (3:1 non-text), 2.4.7 (focus visible), 2.4.11 (focus not obscured, AA), 2.5.8 (target 24px, AA), 2.4.13 (focus appearance, AAA — program house rule). axe-core for the automatable checks on rendered HTML. Spec-vs-realized: this gate judges the rendered result; the design-system gate judges the stated per-component contract.

## Fidelity, seed, conformance, content, states, responsive, versioning
- Same source families as the author sibling: NN/g fidelity model; Vercel v0 "90% problem" + UXPin/Anima no-handoff (seed-not-prod); shadcn/Tailwind/DTCG (token→code conformance); the lorem-ipsum content-design consensus + skeleton-vs-spinner literature (content + states); mobile-first + content-driven breakpoints (responsive); design-as-code semver + Keep-a-Changelog (the delta-review version bar).

## Polish heuristics
- The five named aesthetic heuristics (balance / whitespace-restraint / rhythm / focal-clarity / cohesion) are the program's deliberate choice (NN/g visual-hierarchy + visual-design fundamentals) — judged but named + articulable; out-of-set subjective taste is excluded from a `revise`.
