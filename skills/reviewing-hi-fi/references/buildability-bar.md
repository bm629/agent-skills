# The hi-fi bar — 13 conditions expanded (depth)

Loaded on demand by `reviewing-hi-fi`. Per-condition pass/gap signals + worked findings. Single-sourced from `authoring-hi-fi`'s Step-6 bar — same conditions, judged on the RENDER.

Always re-render the code + vision-review the fresh result before judging (cond. 6 is the mechanism, not a step you can skip).

## cond-1 — Full coverage vs the wireframes (baseline)
- Pass: every wireframe-named screen + flow-visited state has a rendered hi-fi screen.
- Gap: a named screen/state un-rendered. Cross-check the wireframes; if absent, judge the doc's inventory + note the missing input.

## cond-2 — Fidelity + scope (baseline)
- Pass: hi-fidelity visuals (looks like a live system), no invented structure/screen/nav, judged as a SEED.
- Gap: still wireframe-grey/default-styled (under-fidelity); a screen/region the wireframe didn't name (over-reach); a production-readiness claim it doesn't meet.
- NOT a gap: missing tests, mock data, CDN, single-file, no real backend — seed allowances.

## cond-3 — Visual execution + hierarchy
- Pass: DS color/type/spacing/elevation/radius/icons/imagery realized; primary element dominant; hierarchy legible.
- Gap: flat/undifferentiated screen; everything competing; unstyled.

## cond-4 — Polish (objective + named heuristics; out-of-set taste excluded)
- Objective pass: grid-aligned, consistent scale, no clipped/overlap/orphan, on-token, sibling-consistent.
- Named heuristics (each articulable): balance, whitespace & restraint, spacing rhythm, focal clarity, aesthetic cohesion.
- Gap: an objective failure OR a NAMED heuristic failure — and the finding states WHICH heuristic + why (e.g. "focal clarity: two equal-weight CTAs compete, no clear primary").
- NOT a gap: "a nicer hue/layout exists" (out-of-set subjective taste). Worked: "revise — cond.4 balance: the dashboard's right rail is empty while the left stacks five dense cards; rebalance" is valid; "revise — I'd prefer teal" is not.

## cond-5 — Token-backed / no DS drift (baseline)
- Pass: every value token-backed (Tailwind token-utility / CSS var / shadcn token); mapping faithful to the DS.
- Gap: a raw `#hex`/`px`/`bg-blue-500` bypassing a token; a local override; an inlined component the DS lacks. Fix is always at the token layer.

## cond-6 — Rendered + vision-reviewed by YOU (baseline; the mechanism)
- Pass: you re-rendered the code, captured a fresh screenshot per viewport×state, and it renders unbroken + matches the wireframe + DS.
- Gap: fails to render / renders broken / diverges from the wireframe. A review off a handed-in image or code-read-only is incomplete (flag a degraded run).

## cond-7 — Content realism (baseline)
- Pass: real representative content; realistic + edge data (long strings, overflow) exercised.
- Gap: lorem/placeholder filler; only-tidy-short data.

## cond-8 — Rendered states + quality
- Pass: each flow-visited state is a rendered screenshot — empty (reason+action), loading (skeleton mirroring the layout, not a bare spinner), populated, error (cause+recovery), success, partial.
- Gap: an applicable state un-rendered or an empty-shell state. Collapse: a static screen has only populated.

## cond-9 — Responsive reflow
- Pass: rendered + correct at the target viewports; mobile content-priority + adaptive nav where it matters; touch targets sized.
- Gap: a responsive surface shown at one width only, or reflow broken on the render. Collapse: a stated single-form-factor surface.

## cond-10 — Numeric WCAG 2.2 AA on the render (spec-vs-realized)
- Pass: axe-core clean (no rule disabled) + on the render: contrast ≥4.5:1 text / ≥3:1 large+UI (1.4.3/1.4.11); focus visible (2.4.7) + not-obscured (2.4.11) + appearance ≥2px/3:1 (2.4.13 house rule); target ≥24px (2.5.8); keyboard + reduced-motion.
- Gap: a measured failure on the render, or a suppressed rule. Fix at the token layer.
- Spec-vs-realized: judge whether the RENDER achieves the threshold — NOT whether the DS doc states it (that's `reviewing-design-system` cond-10's job). No double-judge.
- Baseline: contrast + landmarks + names always; focus/target/motion where interactive/animated.

## cond-11 — DS conformance (baseline)
- Pass: the rendered result conforms to the DS (components are the DS's or faithful; no contradiction).
- Gap: a rendered component contradicting the DS contract. Out-of-lane: grading the DS's OWN quality — surface + route to the DS gate.

## cond-12 — Gaps surfaced, not invented
- Pass: undefined screen/content, missing DS token/component, a degraded (no-render) run = explicit assumptions.
- Gap: papering a gap with an invented token/component or a faked screenshot.

## cond-13 — Delta-scoped review (amended hi-fi only; N/A greenfield)
- Pass: diff + re-rendered changed screens reviewed; scope-confined (untouched screens' code byte-stable, their screenshots not re-captured); ripple-clean (token change reached ALL consumers, none hand-edited off-token, every changed screen's screenshot re-captured, no newly un-rendered screen, no name drift); changed screens re-vision-reviewed (still meet polish + WCAG + DS-conformance); version + changelog correct (renamed/removed screen OR state = MAJOR); breaking removal carries deprecation.
- Gap: any of the above — e.g. a token changed but one consuming screen left stale, or a screenshot not re-captured.

## Verdict discipline
- approve: every applicable condition passes on the render (a thin seed with collapsed conditions still approves).
- revise: ≥1 real, named, rendered gap. Never on out-of-set taste (cond.4), DS quality (cond.11), or seed-only gaps (cond.2). One literal `VERDICT: approve|revise` line; every revise finding = failed condition + location (screen/state/viewport) + concrete fix (token-layer where applicable).
