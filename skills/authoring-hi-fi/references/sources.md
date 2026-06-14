# Sources & provenance — `authoring-hi-fi`

Portable provenance for the method + the bar. Triangulated across reputable independent sources; nothing operational lifted.

## Fidelity model & when hi-fi
- Nielsen Norman Group — "UX Prototypes: Low Fidelity vs. High Fidelity" (the 3-axis fidelity model: interactivity / visuals / content & navigation; hi-fi = HIGH visuals + HIGH content + real interactivity; when hi-fi is worth it — test workflow, UI components, affordance, page hierarchy, type legibility, image quality, engagement). NN/g "IA-Based View of Prototype Fidelity".

## Hi-fi-as-code is a build SEED (not production)
- Vercel v0 — "Introducing the new v0" + the "90% problem" coverage: original v0 produced prototype scaffolding that lived outside real codebases and required rewrites before production. The seed is reused for its visual language, not shipped as-is.
- UXPin Merge / Anima — code-backed design + the "no-handoff" / "design-drift" framing: designers + developers on separate component versions cause drift; the closer the design code sits to the build stack, the less drift.

## The render → vision-review → refine loop (design-to-code research)
- ReLook — vision-grounded RL with a multimodal-LLM critic for agentic web coding (generate–diagnose–refine; the MLLM scores code with screenshots + gives actionable vision-grounded feedback).
- "Vision-Guided Iterative Refinement for Frontend Code Generation" — visual self-revision prompting (condition on screenshots of the target AND the model's own render; revise to match).
- DesignCoder (browser-screenshot self-inspection), UICoder (compile-render-CLIP feedback), VisRefiner (learning from visual differences).
- Design2Code / Sketch2Code benchmarks; UI2Code^N (VLM-judge rankings track human evaluation). A fast-moving area — re-check current best before relying on specific model claims.

## Token → code
- shadcn/ui — Theming docs (CSS-variable theming, `tailwind.cssVariables`, semantic tokens, `hsl(var(--token))`, `.dark`); Tailwind v4 `@theme` integration.
- W3C Design Tokens Community Group (DTCG) — the design-tokens format (primitive/semantic/component tiers, `$`-prefixed JSON); Style Dictionary (v4+ DTCG support) generating CSS-var output.

## Content realism & states
- The "death to lorem ipsum" content-design consensus (placeholder text can't size the layout truthfully, is invisible to screen-reader review, hides tone; "if you haven't done the writing, the design isn't done").
- Skeleton-vs-spinner perceived-performance literature (a skeleton mirroring the content cuts perceived load ~30–50% + prevents layout shift; spinner for short discrete actions; an error state is mandatory). NN/g empty-state guidance (reason + guide-to-action).

## Accessibility (numeric, on the render)
- W3C WCAG 2.2 — SC 1.4.3 Contrast (Minimum, AA), 1.4.11 Non-text Contrast (AA), 2.4.7 Focus Visible (AA), 2.4.11 Focus Not Obscured Minimum (AA), 2.5.8 Target Size Minimum (AA, 24px), 2.4.13 Focus Appearance (AAA — adopted as a program house rule). axe-core for automated checks on the rendered HTML.

## Responsive & mobile
- Mobile-first responsive practice (design smallest-first; content-priority decisions — promote/demote/hide; adaptive nav → hamburger/off-canvas); content-driven breakpoints (~360/768/1024/1280); device-frame mockups (phone-frame to lock the mobile look; real native preview is infra-bound + deferred).

## Versioning
- Treat design like source code — semantic versioning + Keep-a-Changelog stored alongside the code; design-system versioning practice (MAJOR/MINOR/PATCH by breaking/additive/fix; deprecate before remove).

## Polish heuristics
- The five named aesthetic heuristics (balance / whitespace-restraint / rhythm / focal-clarity / cohesion) are a deliberate program choice drawing on NN/g visual-hierarchy + visual-design fundamentals — judged but named + articulable; subjective out-of-set taste is excluded.
