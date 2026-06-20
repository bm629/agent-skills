# reviewing-hi-fi

Judge a **finished (or amended) high-fidelity UI design produced AS CODE** and decide whether it is a sound build seed — an acceptance gate, not authoring. The review half of the hi-fi pair; the reviewer **re-renders the code itself** (headless browser) and vision-reviews the fresh screenshots, never trusting handed-in images. It single-sources its bar from the same research as `authoring-hi-fi`. Requires a vision-capable runtime.

## Purpose

A hi-fi design-as-code can read fine and render broken; a handed-in screenshot can be stale or cherry-picked. Before the hi-fi seeds the build, something has to decide whether the *rendered* result is sound: covers every wireframe-named screen, is visually realized to the bar, is accessible on the render, and conforms to the design-system. This skill is that gate. It re-renders the code, captures a fresh screenshot per viewport × state, vision-reviews the fresh render against a fixed checklist, and emits a single machine-parseable verdict — so produce → review → accept can run as a loop.

## When to activate

- ✅ A finished hi-fi design-as-code needs an accept/revise decision before the human visual gate / the build milestone.
- ✅ You are the independent reviewer / gate for a hi-fi a producer just rendered.
- ✅ Re-judging a revised hi-fi after a prior `revise`, or reviewing an **amended** hi-fi as a scoped delta.

### When NOT to activate

- **Authoring or repairing a hi-fi** → `authoring-hi-fi` (this skill never writes or re-renders to improve).
- **Judging the screen structure** (layout regions, component selection, states-as-structure) → `reviewing-wireframes`.
- **Judging the token system / component catalog / per-component a11y contract** → `reviewing-design-system` (this gate checks the rendered result *conforms*).
- **Re-deciding which screens/transitions exist** → user-flows.
- **Judging final production code** (tests, real backend, perf) → this is a seed; the build phase owns that.

## The bar (14 conditions)

Re-render the code, then judge each condition on the **fresh render** (not the code text alone), proportional to the screen's archetype: (1) **full coverage** vs the wireframes — every named screen + flow-visited state rendered; (2) **fidelity + scope** — hi-fidelity (not wireframe-grey), no invented structure, judged as a seed (not revised for missing tests/backend, not approved if claiming production-readiness); (3) **visual execution + hierarchy** — DS visual language realized, primary element dominant; (4) **polish** — the objective subset + the five named heuristics (balance, whitespace & restraint, spacing rhythm, focal clarity, aesthetic cohesion; subjective taste is never a gap); (5) **token-backed / no DS drift** — every value traces to a token, no raw hex/px/override; (6) **rendered + vision-reviewed by you** — re-rendered, fresh screenshot, renders without breakage; (7) **content realism** — real + edge data, no lorem; (8) **rendered states + quality** — each flow-visited state rendered (skeleton not spinner, error = cause + recovery); (9) **responsive reflow** at the target viewports; (10) **numeric WCAG 2.2 AA on the render** — axe-core clean with no rule disabled + contrast/focus/target/keyboard/reduced-motion judged on the render (spec-vs-realized); (11) **DS conformance** — the render conforms (DS's own quality is out-of-lane); (12) **gaps surfaced, not invented**; (13) **delta-scoped review** (amended hi-fi only) — diff + ripple + re-vision-review the changed screens, version + changelog correct (n/a greenfield).

## Output

Exactly one verdict line — the literal `VERDICT: approve` or `VERDICT: revise` on its own line — plus findings. On `revise`, every finding is **actionable**: the failed condition, the exact location (which screen / state / viewport), and **how to fix it** (at the token layer for a contrast/token issue). On `approve`, findings are optional non-blocking notes. **Approves** a seed meeting every applicable condition (no false-revise on a thin screen); **revises** only on a real, named, rendered gap.

## Key guarantees

- **Re-renders; never trusts a handed-in screenshot** — renders the code itself + vision-reviews the fresh result; that mechanism IS the gate.
- **Single-sourced bar** — the same 14 conditions the author produces to; no private stricter standard, no invented extra condition.
- **No false-revise** — out-of-set subjective taste is never a gap; seed-only gaps (no tests/backend) are never a gap.
- **No false-approve** — an un-rendered screen, off-token raw value, contrast failure on the render, lorem, or invented token/component is a `revise`.
- **Stays in lane** — judges the render's WCAG + DS conformance (spec-vs-realized); never grades the design-system's own contract or the screen structure.
- **capability-record-aware** — when a `capability_record` is injected by the authoring caller, judgment includes a capability-boundary condition (design-system tokens only, boundary matches wireframes scope); n/a when no record was injected.
- **Machine-parseable verdict** — the exact `VERDICT:` line a loop can read.

## License

MIT © 2026 Bhushan Modi.
